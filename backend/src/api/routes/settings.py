from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from pathlib import Path

router = APIRouter(prefix="/settings", tags=["settings"])

# Pydantic models
class NetworkSettingsRequest(BaseModel):
    network: str  # 'devnet' or 'mainnet'
    rpc_endpoint: str
    ws_endpoint: str

class NetworkSettingsResponse(BaseModel):
    network: str
    rpc_endpoint: str
    ws_endpoint: str

# Get current network settings
@router.get("/network", response_model=NetworkSettingsResponse)
def get_network_settings():
    """Get current network configuration"""
    try:
        # Read from config.py or environment
        from config import RPC_ENDPOINT, WS_ENDPOINT

        # Determine network from endpoint
        network = 'mainnet' if 'mainnet' in RPC_ENDPOINT else 'devnet'

        return {
            "network": network,
            "rpc_endpoint": RPC_ENDPOINT,
            "ws_endpoint": WS_ENDPOINT
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update network settings
@router.post("/network")
def update_network_settings(request: NetworkSettingsRequest):
    """
    Update network configuration

    This updates the .env file with new network settings.
    Server restart is required for changes to take effect.
    """
    try:
        # Path to .env file
        env_path = Path(__file__).parent.parent.parent.parent / '.env'

        # Read existing .env content
        env_content = {}
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_content[key] = value

        # Update network settings
        env_content['RPC_ENDPOINT'] = request.rpc_endpoint
        env_content['WS_ENDPOINT'] = request.ws_endpoint

        # Write back to .env
        with open(env_path, 'w') as f:
            f.write("# Solana Network Configuration\n")
            f.write(f"# Current Network: {request.network.upper()}\n\n")

            for key, value in env_content.items():
                f.write(f"{key}={value}\n")

        return {
            "success": True,
            "message": f"Network settings updated to {request.network}",
            "network": request.network,
            "rpc_endpoint": request.rpc_endpoint,
            "ws_endpoint": request.ws_endpoint,
            "note": "Please restart the backend server for changes to take effect"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
