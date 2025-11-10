from __future__ import absolute_import
from __future__ import print_function
from gocd import Server

server = Server('http://localhost:8153', 'admin', 'badger')
pipeline = server.pipeline('PHP')

# response = pipeline.status()
# print(response.is_ok)

# response = pipeline.history(10);
# print(response)
# print(response.is_ok)

# stage = server.stage('PHP', 'Configure', 36)
# response= stage.run()
# print(response.is_ok)

stage = server.stage('PHP', 'Configure', 36)
response= stage.cancel(16)
print(response.is_ok)

# response = pipeline.pause('Admin says no work for you.')
# response.is_ok

# unpause_response = pipeline.unpause()
# unpause_response.is_ok


# response = pipeline.schedule()
# print(response.is_ok)

# response = pipeline.schedule({"name":"username", "value":"bob"})
# print((response.is_ok))
