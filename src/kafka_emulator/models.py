from pydantic import BaseModel, model_validator


class KafkaDefault(BaseModel):
    bootstrap_servers: str = "localhost:9092"


class KafkaConfig(BaseModel):
    default: KafkaDefault = KafkaDefault()


class Defaults(BaseModel):
    headers: dict[str, str] = {}


class SendStep(BaseModel):
    topic: str
    body: str
    key: str | None = None
    headers: dict[str, str] = {}


class SleepStep(BaseModel):
    message: str | None = None
    duration: str = "0ms"


class PauseStep(BaseModel):
    message: str | None = None
    timeout: str | None = None


class Step(BaseModel):
    set: dict[str, str] | None = None
    send: SendStep | None = None
    sleep: SleepStep | None = None
    pause: PauseStep | None = None

    @model_validator(mode="after")
    def exactly_one_step(self):
        fields = [self.set, self.send, self.sleep, self.pause]
        count = sum(1 for f in fields if f is not None)
        if count != 1:
            raise ValueError(
                "Each step must have exactly one of:"
                " set, send, sleep, pause"
            )
        return self


class Scenario(BaseModel):
    name: str = "unnamed"
    kafka: KafkaConfig = KafkaConfig()
    defaults: Defaults = Defaults()
    steps: list[Step]
