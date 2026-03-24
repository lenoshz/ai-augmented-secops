"""Alert payload models for ECS-normalized alerts."""

from typing import Any

from pydantic import BaseModel, Field


class AlertPayload(BaseModel):
    """Input alert payload carrying key ECS fields and raw content."""

    alert_id: str = Field(default="", description="Unique alert identifier.")
    timestamp: str = Field(default="", alias="@timestamp", description="Alert timestamp.")
    rule_name: str = Field(default="", description="Detection rule name.")
    rule_id: str = Field(default="", description="Detection rule identifier.")
    host_name: str = Field(default="", description="Host name for affected asset.")
    user_name: str = Field(default="", description="User name associated with alert.")
    event_category: str = Field(default="", description="Event category in ECS.")
    event_action: str = Field(default="", description="Event action in ECS.")
    source_ip: str = Field(default="", description="Source IP address.")
    destination_ip: str = Field(default="", description="Destination IP address.")
    process_name: str = Field(default="", description="Process executable or image name.")
    file_name: str = Field(default="", description="File involved in alert.")
    severity: str = Field(default="medium", description="Reported alert severity.")
    raw_event: dict[str, Any] = Field(default_factory=dict, description="Original alert document.")

    model_config = {"populate_by_name": True, "extra": "allow"}
