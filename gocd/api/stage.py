from gocd.api.endpoint import Endpoint

__all__ = ['Stage']


class Stage(Endpoint):
    base_path = 'go/api/stages/{id}'

    def __init__(self, server, pipeline_name, stage_name, pipeline_counter=None,
        stage_counter=None):
        """A wrapper for the `Go stage API`__

        .. __: http://api.go.cd/current/#stages
        details: only 1 API - to run a stage, stage_counter is not used

        .. __: http://api.go.cd/current/#stage-instances
        details: 5 APIs, stage_counter is used in 4/5 of them

        Args:
          server (Server): A configured instance of
            :class:gocd.server.Server
          pipeline_name (str): The name of the pipeline we're working on
          stage_name (str): The name of the stage we're working on
        """
        self.server = server
        self.pipeline_name = pipeline_name
        self.pipeline_counter = pipeline_counter
        self.stage_name = stage_name
        self.stage_counter = stage_counter
        self.assist_in_getting_id = True

    def get_id(self):
        if not self.assist_in_getting_id:
            return ""

        if self.pipeline_name is None or self.pipeline_counter is None or self.stage_name is None:
            raise Exception('You must provide a pipeline name, a pipeline counter, and a stage '
                            'name')

        return "{pipeline_name}/{pipeline_counter}/{stage_name}".format(
            pipeline_name=self.pipeline_name,
            pipeline_counter=self.pipeline_counter,
            stage_name=self.stage_name
        )

    def run(self):
        """Runs a specified stage

        See the `Go stage run documentation`__ for example responses.

        .. __: https://api.gocd.org/current/#run-stage

        Args:
          pipeline_name (str): Name of the pipeline.
          pipeline_counter (int): Name of the pipeline.
          stage_name (str): Name of the pipeline.

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """

        return self._post('/run', 202, headers={
            "X-GoCD-Confirm": "true",
            "Accept": "application/vnd.go.cd.v2+json"},
                          method="POST"
                          )

    def cancel(self, stage_counter=None):
        """Cancels a currently running stage

        See the `Go stage cancel documentation`__ for example responses.

        .. __: https://api.gocd.org/current/#cancel-stage

        Args:
          stage_counter (int): Name of the pipeline.

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """

        if stage_counter is None:
            raise Exception('You must provide a stage counter')

        if type(stage_counter) is not int:
            raise Exception('Stage counter must be an integer')

        path = f'/{stage_counter}/cancel'

        return self._post(path, headers={
            "X-GoCD-Confirm": "true", "Accept":
                "application/vnd.go.cd.v3+json"},
                          method="POST"
                          )

    def history(self, offset=0):
        """Lists previous instances/runs of the stage

        See the `Go stage history documentation`__ for example responses.

        .. __: http://api.go.cd/current/#get-stage-history

        Args:
          offset (int, optional): How many instances to skip for this response.

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """
        return self._get('/history/{offset:d}'.format(offset=offset or 0))

    def instance(self, stage_counter=None):
        """Returns all the information regarding a specific stage run

        See the `Go stage instance documentation`__ for examples.

        .. __: http://api.go.cd/current/#get-stage-instance

        Args:
          stage_counter (int): The stage instance to fetch.
            If falsey returns the latest stage instance from :meth:`history`.

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """

        if not stage_counter:
            raise Exception('You must provide a stage counter')

        return self._get('/instance/{pipeline_counter:d}/{counter:d}'
                         .format(pipeline_counter=pipeline_counter, counter=counter))
