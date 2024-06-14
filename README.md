# Metis Python Client

This Python client is designed to provide developers with a seamless integration into the Metisai api platform, enabling the efficient management and customization of generative AI-driven chatbots and image generation models.

## Features

- **API Integration**: Easy access to Metis's API endpoints for model selection, configuration, and management.
- **Model Customization**: Tools to customize and fine-tune large language models (LLMs) for text and image generation according to specific requirements.
- **Monitoring**: Capabilities to monitor the performance and quality of AI models, ensuring optimal functionality.
- **Simplified Deployment**: Streamlined processes for transitioning from model development to production.

## Installation

To install the Metis Python Client, run the following command:

```bash
pip install metisai
```

## Usage

### Session
Here’s a quick example of how to use the client to interact with Metis:

```python
import metisai

# Initialize the client
metisbot = metisai.MetisBot(api_key=METIS_API_KEY, bot_id=METIS_BOT_ID)

# Initialize a session
session = metisbot.create_session()
message = metisbot.send_message(session, "Suggest me a list of 5 gifts for a 30 years boy who is tech-fan.")
print(message.content)
message2 = metisbot.send_message(session, "What if he is a book lover?")
print(message2.content)

# Delete a session
metisbot.delete_session(session)
```

### Async
Here’s an example of async operation (this is not `asyncio`):

```python
import metisai

# Initialize the client
metisbot = metisai.MetisBot(api_key=METIS_API_KEY, bot_id=METIS_BOT_ID)

prompt = "Suggest me a list of 5 gifts for a 30 years boy who is tech-fan."
session = metisbot.create_session()
task = metisbot.send_message_async(session, prompt)

while True:
    task_result = metisbot.retrieve_async_task(session, task)
    if task_result.status == "FINISHED":
        break
    time.sleep(1)
print(task_result.message.content)
print()
metisbot.delete_session(session)
```

### Stream
Here’s an example of stream usage:

```python
import metisai

# Initialize the client
metisbot = metisai.MetisBot(api_key=METIS_API_KEY, bot_id=METIS_BOT_ID)

prompt = "Suggest me a list of 5 gifts for a 30 years boy who is tech-fan."
stream = metisbot.stream_messages(
    session, prompt, split_criteria={"line": True}
)
for message in stream:
    print(message.message.content)
metisbot.delete_session(session)
```


## Configuration
Before using the client, ensure you configure it with your API key:

```python
metisbot = metisai.MetisBot(api_key=METIS_API_KEY, bot_id=METIS_BOT_ID)
```

## Documentation
For more detailed information about the client's methods and additional functionalities, refer to the [Metis Documentation](https://docs.metisai.ir/).

## Support
If you encounter any issues or have questions, please contact hello@metisai.ir.

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/mahdikiani/metisai/blob/main/LICENSE) file for details.