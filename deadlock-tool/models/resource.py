class Resource:
    def __init__(self, resource_id: str, total_instances: int = 1):
        self.resource_id = resource_id
        self.total_instances = total_instances
        self.allocated_instances = 0

    @property
    def available_instances(self) -> int:
        return self.total_instances - self.allocated_instances

    def allocate(self, count: int = 1) -> bool:
        if count > self.available_instances:
            return False
        self.allocated_instances += count
        return True

    def release(self, count: int = 1) -> None:
        self.allocated_instances = max(0, self.allocated_instances - count)

    def __repr__(self) -> str:
        return (f"Resource({self.resource_id}, total={self.total_instances}, "
                f"allocated={self.allocated_instances})")
