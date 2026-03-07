from gocd import Server

import json

USERNAME = 'admin'
PASSWORD = 'badger'
PIPELINE_NAME = 'up42'
PIPELINE_COUNTER = 1
STAGE_NAME = 'up42_stage'
STAGE_COUNTER = 1

server = Server('http://localhost:8153', USERNAME, PASSWORD)

pipeline = server.pipeline(PIPELINE_NAME)
response = pipeline.status()
print(response.is_ok)

# response = pipeline.instance(23)
# print(response.is_ok)

# response = pipeline.history()
# print(response.is_ok)

# history = response["pipelines"]

# response = pipeline.history(10);
# print(response)
# print(response.is_ok)

# stage = server.stage('up42', 'up42_stage', 40)
# response = stage.history()
# response= stage.run()
# response = stage.instance(40)
# print(response.is_ok)

# stage = server.stage('PHP', 'Configure', 36)
# response= stage.cancel(16)
# print(response.is_ok)

# response = pipeline.pause('Admin says no work for you.')
# print(response.is_ok)

# unpause_response = pipeline.unpause()
# print(unpause_response.is_ok)

# response = pipeline.schedule()
# print(response.is_ok)

# response = pipeline.schedule({"name":"username", "value":"bob"})
# print((response.is_ok))
