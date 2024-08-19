import logging
import os
import shutil
import tempfile
from typing import List

from fastapi import APIRouter, Depends, File, Form, UploadFile

from gptdb._private.config import Config
from gptdb.app.knowledge.request.request import (
    ChunkQueryRequest,
    DocumentQueryRequest,
    DocumentSummaryRequest,
    DocumentSyncRequest,
    EntityExtractRequest,
    GraphVisRequest,
    KnowledgeDocumentRequest,
    KnowledgeQueryRequest,
    KnowledgeSpaceRequest,
    SpaceArgumentRequest,
)
from gptdb.app.knowledge.request.response import KnowledgeQueryResponse
from gptdb.app.knowledge.service import KnowledgeService
from gptdb.app.openapi.api_v1.api_v1 import no_stream_generator, stream_generator
from gptdb.app.openapi.api_view_model import Result
from gptdb.configs import TAG_KEY_KNOWLEDGE_FACTORY_DOMAIN_TYPE
from gptdb.configs.model_config import (
    EMBEDDING_MODEL_CONFIG,
    KNOWLEDGE_UPLOAD_ROOT_PATH,
)
from gptdb.core.awel.dag.dag_manager import DAGManager
from gptdb.rag import ChunkParameters
from gptdb.rag.embedding.embedding_factory import EmbeddingFactory
from gptdb.rag.knowledge.base import ChunkStrategy
from gptdb.rag.knowledge.factory import KnowledgeFactory
from gptdb.rag.retriever.embedding import EmbeddingRetriever
from gptdb.serve.rag.api.schemas import (
    KnowledgeConfigResponse,
    KnowledgeDomainType,
    KnowledgeStorageType,
    KnowledgeSyncRequest,
)
from gptdb.serve.rag.connector import VectorStoreConnector
from gptdb.serve.rag.service.service import Service
from gptdb.storage.vector_store.base import VectorStoreConfig
from gptdb.util.i18n_utils import _
from gptdb.util.tracer import SpanType, root_tracer

logger = logging.getLogger(__name__)

CFG = Config()
router = APIRouter()


knowledge_space_service = KnowledgeService()


def get_rag_service() -> Service:
    """Get Rag Service."""
    return Service.get_instance(CFG.SYSTEM_APP)


def get_dag_manager() -> DAGManager:
    """Get DAG Manager."""
    return DAGManager.get_instance(CFG.SYSTEM_APP)


@router.post("/knowledge/space/add")
def space_add(request: KnowledgeSpaceRequest):
    print(f"/space/add params: {request}")
    try:
        knowledge_space_service.create_knowledge_space(request)
        return Result.succ([])
    except Exception as e:
        return Result.failed(code="E000X", msg=f"space add error {e}")


@router.post("/knowledge/space/list")
def space_list(request: KnowledgeSpaceRequest):
    print(f"/space/list params:")
    try:
        return Result.succ(knowledge_space_service.get_knowledge_space(request))
    except Exception as e:
        return Result.failed(code="E000X", msg=f"space list error {e}")


@router.post("/knowledge/space/delete")
def space_delete(request: KnowledgeSpaceRequest):
    print(f"/space/delete params:")
    try:
        return Result.succ(knowledge_space_service.delete_space(request.name))
    except Exception as e:
        return Result.failed(code="E000X", msg=f"space delete error {e}")


@router.post("/knowledge/{space_name}/arguments")
def arguments(space_name: str):
    print(f"/knowledge/space/arguments params:")
    try:
        return Result.succ(knowledge_space_service.arguments(space_name))
    except Exception as e:
        return Result.failed(code="E000X", msg=f"space arguments error {e}")


@router.post("/knowledge/{space_name}/argument/save")
def arguments_save(space_name: str, argument_request: SpaceArgumentRequest):
    print(f"/knowledge/space/argument/save params:")
    try:
        return Result.succ(
            knowledge_space_service.argument_save(space_name, argument_request)
        )
    except Exception as e:
        return Result.failed(code="E000X", msg=f"space save error {e}")


@router.post("/knowledge/{space_name}/document/add")
def document_add(space_name: str, request: KnowledgeDocumentRequest):
    print(f"/document/add params: {space_name}, {request}")
    try:
        return Result.succ(
            knowledge_space_service.create_knowledge_document(
                space=space_name, request=request
            )
        )
        # return Result.succ([])
    except Exception as e:
        return Result.failed(code="E000X", msg=f"document add error {e}")


@router.get("/knowledge/document/chunkstrategies")
def chunk_strategies():
    """Get chunk strategies"""
    print(f"/document/chunkstrategies:")
    try:
        return Result.succ(
            [
                {
                    "strategy": strategy.name,
                    "name": strategy.value[2],
                    "description": strategy.value[3],
                    "parameters": strategy.value[1],
                    "suffix": [
                        knowledge.document_type().value
                        for knowledge in KnowledgeFactory.subclasses()
                        if strategy in knowledge.support_chunk_strategy()
                        and knowledge.document_type() is not None
                    ],
                    "type": set(
                        [
                            knowledge.type().value
                            for knowledge in KnowledgeFactory.subclasses()
                            if strategy in knowledge.support_chunk_strategy()
                        ]
                    ),
                }
                for strategy in ChunkStrategy
            ]
        )
    except Exception as e:
        return Result.failed(code="E000X", msg=f"chunk strategies error {e}")


@router.get("/knowledge/space/config", response_model=Result[KnowledgeConfigResponse])
async def space_config() -> Result[KnowledgeConfigResponse]:
    """Get space config"""
    try:
        storage_list: List[KnowledgeStorageType] = []
        dag_manager: DAGManager = get_dag_manager()
        # Vector Storage
        vs_domain_types = [KnowledgeDomainType(name="Normal", desc="Normal")]
        dag_map = dag_manager.get_dags_by_tag_key(TAG_KEY_KNOWLEDGE_FACTORY_DOMAIN_TYPE)
        for domain_type, dags in dag_map.items():
            vs_domain_types.append(
                KnowledgeDomainType(
                    name=domain_type, desc=dags[0].description or domain_type
                )
            )

        storage_list.append(
            KnowledgeStorageType(
                name="VectorStore",
                desc=_("Vector Store"),
                domain_types=vs_domain_types,
            )
        )
        # Graph Storage
        storage_list.append(
            KnowledgeStorageType(
                name="KnowledgeGraph",
                desc=_("Knowledge Graph"),
                domain_types=[KnowledgeDomainType(name="Normal", desc="Normal")],
            )
        )
        # Full Text
        storage_list.append(
            KnowledgeStorageType(
                name="FullText",
                desc=_("Full Text"),
                domain_types=[KnowledgeDomainType(name="Normal", desc="Normal")],
            )
        )

        return Result.succ(
            KnowledgeConfigResponse(
                storage=storage_list,
            )
        )
    except Exception as e:
        return Result.failed(code="E000X", msg=f"space config error {e}")


@router.post("/knowledge/{space_name}/document/list")
def document_list(space_name: str, query_request: DocumentQueryRequest):
    print(f"/document/list params: {space_name}, {query_request}")
    try:
        return Result.succ(
            knowledge_space_service.get_knowledge_documents(space_name, query_request)
        )
    except Exception as e:
        return Result.failed(code="E000X", msg=f"document list error {e}")


@router.post("/knowledge/{space_name}/graphvis")
def graph_vis(space_name: str, query_request: GraphVisRequest):
    print(f"/document/list params: {space_name}, {query_request}")
    print(query_request.limit)
    try:
        return Result.succ(
            knowledge_space_service.query_graph(
                space_name=space_name, limit=query_request.limit
            )
        )
    except Exception as e:
        return Result.failed(code="E000X", msg=f"get graph vis error {e}")


@router.post("/knowledge/{space_name}/document/delete")
def document_delete(space_name: str, query_request: DocumentQueryRequest):
    print(f"/document/list params: {space_name}, {query_request}")
    try:
        return Result.succ(
            knowledge_space_service.delete_document(space_name, query_request.doc_name)
        )
    except Exception as e:
        return Result.failed(code="E000X", msg=f"document delete error {e}")


@router.post("/knowledge/{space_name}/document/upload")
async def document_upload(
    space_name: str,
    doc_name: str = Form(...),
    doc_type: str = Form(...),
    doc_file: UploadFile = File(...),
):
    print(f"/document/upload params: {space_name}")
    try:
        if doc_file:
            if not os.path.exists(os.path.join(KNOWLEDGE_UPLOAD_ROOT_PATH, space_name)):
                os.makedirs(os.path.join(KNOWLEDGE_UPLOAD_ROOT_PATH, space_name))
            # We can not move temp file in windows system when we open file in context of `with`
            tmp_fd, tmp_path = tempfile.mkstemp(
                dir=os.path.join(KNOWLEDGE_UPLOAD_ROOT_PATH, space_name)
            )
            with os.fdopen(tmp_fd, "wb") as tmp:
                tmp.write(await doc_file.read())
            shutil.move(
                tmp_path,
                os.path.join(KNOWLEDGE_UPLOAD_ROOT_PATH, space_name, doc_file.filename),
            )
            request = KnowledgeDocumentRequest()
            request.doc_name = doc_name
            request.doc_type = doc_type
            request.content = os.path.join(
                KNOWLEDGE_UPLOAD_ROOT_PATH, space_name, doc_file.filename
            )
            space_res = knowledge_space_service.get_knowledge_space(
                KnowledgeSpaceRequest(name=space_name)
            )
            if len(space_res) == 0:
                # create default space
                if "default" != space_name:
                    raise Exception(f"you have not create your knowledge space.")
                knowledge_space_service.create_knowledge_space(
                    KnowledgeSpaceRequest(
                        name=space_name,
                        desc="first gpt-db rag application",
                        owner="gptdb",
                    )
                )
            return Result.succ(
                knowledge_space_service.create_knowledge_document(
                    space=space_name, request=request
                )
            )
        return Result.failed(code="E000X", msg=f"doc_file is None")
    except Exception as e:
        return Result.failed(code="E000X", msg=f"document add error {e}")


@router.post("/knowledge/{space_name}/document/sync")
async def document_sync(
    space_name: str,
    request: DocumentSyncRequest,
    service: Service = Depends(get_rag_service),
):
    logger.info(f"Received params: {space_name}, {request}")
    try:
        space = service.get({"name": space_name})
        if space is None:
            return Result.failed(code="E000X", msg=f"space {space_name} not exist")
        if request.doc_ids is None or len(request.doc_ids) == 0:
            return Result.failed(code="E000X", msg="doc_ids is None")
        sync_request = KnowledgeSyncRequest(
            doc_id=request.doc_ids[0],
            space_id=str(space.id),
            model_name=request.model_name,
        )
        sync_request.chunk_parameters = ChunkParameters(
            chunk_strategy="Automatic",
            chunk_size=request.chunk_size or 512,
            chunk_overlap=request.chunk_overlap or 50,
        )
        doc_ids = await service.sync_document(requests=[sync_request])
        return Result.succ(doc_ids)
    except Exception as e:
        return Result.failed(code="E000X", msg=f"document sync error {e}")


@router.post("/knowledge/{space_name}/document/sync_batch")
async def batch_document_sync(
    space_name: str,
    request: List[KnowledgeSyncRequest],
    service: Service = Depends(get_rag_service),
):
    logger.info(f"Received params: {space_name}, {request}")
    try:
        space = service.get({"name": space_name})
        for sync_request in request:
            sync_request.space_id = space.id
        doc_ids = await service.sync_document(requests=request)
        # doc_ids = service.sync_document(
        #     space_name=space_name, sync_requests=request
        # )
        return Result.succ({"tasks": doc_ids})
    except Exception as e:
        return Result.failed(code="E000X", msg=f"document sync batch error {e}")


@router.post("/knowledge/{space_name}/chunk/list")
def document_list(space_name: str, query_request: ChunkQueryRequest):
    print(f"/document/list params: {space_name}, {query_request}")
    try:
        return Result.succ(knowledge_space_service.get_document_chunks(query_request))
    except Exception as e:
        return Result.failed(code="E000X", msg=f"document chunk list error {e}")


@router.post("/knowledge/{vector_name}/query")
def similar_query(space_name: str, query_request: KnowledgeQueryRequest):
    print(f"Received params: {space_name}, {query_request}")
    embedding_factory = CFG.SYSTEM_APP.get_component(
        "embedding_factory", EmbeddingFactory
    )
    config = VectorStoreConfig(
        name=space_name,
        embedding_fn=embedding_factory.create(
            EMBEDDING_MODEL_CONFIG[CFG.EMBEDDING_MODEL]
        ),
    )
    vector_store_connector = VectorStoreConnector(
        vector_store_type=CFG.VECTOR_STORE_TYPE,
        vector_store_config=config,
    )
    retriever = EmbeddingRetriever(
        top_k=query_request.top_k, index_store=vector_store_connector.index_client
    )
    chunks = retriever.retrieve(query_request.query)
    res = [
        KnowledgeQueryResponse(text=d.content, source=d.metadata["source"])
        for d in chunks
    ]
    return {"response": res}


@router.post("/knowledge/document/summary")
async def document_summary(request: DocumentSummaryRequest):
    print(f"/document/summary params: {request}")
    try:
        with root_tracer.start_span(
            "get_chat_instance", span_type=SpanType.CHAT, metadata=request
        ):
            chat = await knowledge_space_service.document_summary(request=request)
        headers = {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Transfer-Encoding": "chunked",
        }
        from starlette.responses import StreamingResponse

        if not chat.prompt_template.stream_out:
            return StreamingResponse(
                no_stream_generator(chat),
                headers=headers,
                media_type="text/event-stream",
            )
        else:
            return StreamingResponse(
                stream_generator(chat, False, request.model_name),
                headers=headers,
                media_type="text/plain",
            )
    except Exception as e:
        return Result.failed(code="E000X", msg=f"document summary error {e}")
