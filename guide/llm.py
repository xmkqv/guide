import asyncio
import json
import re
import subprocess
from typing import Any, Literal

from pydantic import BaseModel, create_model


async def aask(*content: str, model: Literal["opus", "sonnet"] = "opus") -> str:
    cmd = (
        "claude",
        "--print",
        *("--model", model),
        *("--max-turns", "10"),
    )

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate(input="\n".join(content).encode())
    stdout = stdout.decode(errors="replace")
    stderr = stderr.decode(errors="replace") if stderr else None

    if process.returncode != 0:
        raise subprocess.CalledProcessError(
            process.returncode or 100, cmd, stdout, stderr
        )
    return stdout


async def aask_model[T: BaseModel](model: type[T], **details: Any) -> T:
    schema = model.model_json_schema()

    prompt = "\n\n".join([f"## {k}\n\n{v}" for k, v in details.items()])

    content = f"""\
**Given the Information and your Knowledge, generate a JSON object Answer**

# Information

{prompt}

# JSON Response Schema

- If there are no valid value(s), use null or empty list/dict befitting the field type
- RESPOND ONLY WITH A SCHEMA VALIDATED JSON OBJECT, DO NOT RESPOND WITH ANY OTHER TEXT
- DO NOT HALLUCINATE

{json.dumps(schema, indent=2)}
"""

    stdout = await aask(content)
    data = re_json.search(stdout)
    data = data.group(1).strip() if data else stdout
    response = model.model_validate_json(data)
    return response


re_json = re.compile(r"```json(.*?)```", re.DOTALL)


def to_required_model[T: BaseModel](original_model: type[T]):
    required_fields = {}
    for field_name, field_info in original_model.model_fields.items():
        if field_info.is_required():
            if field_info.annotation and issubclass(field_info.annotation, BaseModel):
                field_info.annotation = to_required_model(field_info.annotation)

            required_fields[field_name] = (
                field_info.annotation,
                field_info,
            )
    return create_model(
        f"_{original_model.__name__}",
        __base__=(BaseModel,),
        **required_fields,  # type: ignore
    )


if __name__ == "__main__":
    import asyncio

    async def main():
        result = await aask(
            "What is the capital of France? WebSearch return 3 links md"
        )
        print(result)

    asyncio.run(main())
