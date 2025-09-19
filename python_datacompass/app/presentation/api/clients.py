"""
Clients API routes.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.core.logging import get_logger
from app.domain.entities.client import Client, ClientSegment, ChurnRisk
from app.domain.repositories.client_repository import IClientRepository
from app.domain.services.client_analysis_service import ClientAnalysisService

logger = get_logger(__name__)

router = APIRouter(prefix="/api/clients", tags=["Clients"])


# Dependency injection
async def get_client_repository() -> IClientRepository:
    """Get client repository dependency."""
    pass


async def get_interaction_repository():
    """Get interaction repository dependency."""
    pass


# Request/Response models
class ClientCreateRequest(BaseModel):
    """Request model for creating a client."""
    whatsapp_number: str
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
    profession: Optional[str] = None
    income: Optional[float] = None


class ClientUpdateRequest(BaseModel):
    """Request model for updating a client."""
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
    profession: Optional[str] = None
    income: Optional[float] = None


class ClientResponse(BaseModel):
    """Response model for client."""
    client: Client
    message: str


class ClientListResponse(BaseModel):
    """Response model for client list."""
    clients: List[Client]
    total: int
    skip: int
    limit: int


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    request: ClientCreateRequest,
    client_repo: IClientRepository = Depends(get_client_repository)
):
    """Create a new client."""
    try:
        # Check if client already exists
        existing_client = await client_repo.get_by_whatsapp_number(request.whatsapp_number)
        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Client with this WhatsApp number already exists"
            )
        
        # Create client entity
        client = Client(
            whatsapp_number=request.whatsapp_number,
            name=request.name,
            email=request.email,
            age=request.age,
            city=request.city,
            profession=request.profession,
            income=request.income
        )
        
        # Save client
        created_client = await client_repo.create(client)
        
        logger.info(f"Client {created_client.id} created successfully")
        
        return ClientResponse(
            client=created_client,
            message="Client created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create client"
        )


@router.get("/", response_model=ClientListResponse)
async def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    segment: Optional[ClientSegment] = None,
    churn_risk: Optional[ChurnRisk] = None,
    search: Optional[str] = None,
    client_repo: IClientRepository = Depends(get_client_repository)
):
    """Get clients with optional filtering and search."""
    try:
        if search:
            clients = await client_repo.search(search)
            # Apply additional filters if needed
            if segment:
                clients = [c for c in clients if c.segment == segment]
            if churn_risk:
                clients = [c for c in clients if c.churn_risk == churn_risk]
            
            # Apply pagination
            total = len(clients)
            clients = clients[skip:skip + limit]
        else:
            clients = await client_repo.get_all(
                skip=skip,
                limit=limit,
                segment=segment,
                churn_risk=churn_risk
            )
            total = await client_repo.count()
        
        return ClientListResponse(
            clients=clients,
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error getting clients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get clients"
        )


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    client_repo: IClientRepository = Depends(get_client_repository)
):
    """Get a specific client by ID."""
    try:
        client = await client_repo.get_by_id(client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        return ClientResponse(
            client=client,
            message="Client retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get client"
        )


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    request: ClientUpdateRequest,
    client_repo: IClientRepository = Depends(get_client_repository)
):
    """Update a client."""
    try:
        client = await client_repo.get_by_id(client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        # Update client profile
        client.update_profile(
            name=request.name,
            email=request.email,
            age=request.age,
            city=request.city,
            profession=request.profession,
            income=request.income
        )
        
        # Save updated client
        updated_client = await client_repo.update(client)
        
        logger.info(f"Client {client_id} updated successfully")
        
        return ClientResponse(
            client=updated_client,
            message="Client updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update client"
        )


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: str,
    client_repo: IClientRepository = Depends(get_client_repository)
):
    """Delete a client."""
    try:
        client = await client_repo.get_by_id(client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        success = await client_repo.delete(client_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete client"
            )
        
        logger.info(f"Client {client_id} deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete client"
        )


@router.get("/{client_id}/analytics")
async def get_client_analytics(
    client_id: str,
    client_repo: IClientRepository = Depends(get_client_repository),
    interaction_repo = Depends(get_interaction_repository)
):
    """Get analytics for a specific client."""
    try:
        client = await client_repo.get_by_id(client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        # Get client analysis service
        analysis_service = ClientAnalysisService(client_repo, interaction_repo)
        
        # Get engagement metrics
        engagement_metrics = await analysis_service.analyze_client_engagement(client_id)
        
        # Get insights
        insights = await analysis_service.get_client_insights(client_id)
        
        return {
            "success": True,
            "data": {
                "client": client,
                "engagement_metrics": engagement_metrics,
                "insights": insights
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client analytics {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get client analytics"
        )


@router.post("/{client_id}/update-analytics")
async def update_client_analytics(
    client_id: str,
    client_repo: IClientRepository = Depends(get_client_repository),
    interaction_repo = Depends(get_interaction_repository)
):
    """Update client analytics (segment and churn risk)."""
    try:
        client = await client_repo.get_by_id(client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        # Get client analysis service
        analysis_service = ClientAnalysisService(client_repo, interaction_repo)
        
        # Update analytics
        updated_client = await analysis_service.update_client_analytics(client_id)
        
        logger.info(f"Client analytics updated for {client_id}")
        
        return {
            "success": True,
            "data": {
                "client": updated_client,
                "message": "Client analytics updated successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client analytics {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update client analytics"
        )


@router.get("/whatsapp/{whatsapp_number}", response_model=ClientResponse)
async def get_client_by_whatsapp(
    whatsapp_number: str,
    client_repo: IClientRepository = Depends(get_client_repository)
):
    """Get client by WhatsApp number."""
    try:
        client = await client_repo.get_by_whatsapp_number(whatsapp_number)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        return ClientResponse(
            client=client,
            message="Client retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client by WhatsApp {whatsapp_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get client"
        )


@router.get("/segments/{segment}", response_model=List[Client])
async def get_clients_by_segment(
    segment: ClientSegment,
    client_repo: IClientRepository = Depends(get_client_repository)
):
    """Get clients by segment."""
    try:
        clients = await client_repo.get_by_segment(segment)
        return clients
        
    except Exception as e:
        logger.error(f"Error getting clients by segment {segment}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get clients by segment"
        )


@router.get("/churn-risk/{risk}", response_model=List[Client])
async def get_clients_by_churn_risk(
    risk: ChurnRisk,
    client_repo: IClientRepository = Depends(get_client_repository)
):
    """Get clients by churn risk."""
    try:
        if risk in [ChurnRisk.HIGH, ChurnRisk.CRITICAL]:
            clients = await client_repo.get_high_risk_clients()
            # Filter by specific risk if needed
            if risk == ChurnRisk.HIGH:
                clients = [c for c in clients if c.churn_risk == ChurnRisk.HIGH]
            elif risk == ChurnRisk.CRITICAL:
                clients = [c for c in clients if c.churn_risk == ChurnRisk.CRITICAL]
        else:
            clients = await client_repo.get_all(churn_risk=risk)
        
        return clients
        
    except Exception as e:
        logger.error(f"Error getting clients by churn risk {risk}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get clients by churn risk"
        )