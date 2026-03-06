import time
from gocd.api.response import Response
from gocd.api.endpoint import Endpoint
from gocd.api.artifact import Artifact
from gocd.api.stage import Stage

__all__ = ['Pipeline']


class Pipeline(Endpoint):
    base_path = 'go/api/pipelines/{id}'
    id = 'name'
    #: The result of a job/stage has been finalised when these values are set
    final_results = ['Passed', 'Failed']

    def __init__(self, server, name):
        """A wrapper for the `Go pipeline API`__

        .. __: http://api.go.cd/current/#pipelines

        Args:
          server (Server): A configured instance of
            :class:gocd.server.Server
          name (str): The name of the pipeline we're working on
        """
        self.server = server
        self.name = name

    def history(self, page_size=0, after=None, before=None):
        """Lists previous instances/runs of the pipeline

        See the `Go pipeline history documentation`__ for example responses.

        .. __: http://api.go.cd/current/#get-pipeline-history

        Args:
          page_size (int, optional): The number of records per page. Can be between 10 and 100. Defaults to 10.
          after (int, optional): The cursor value for fetching the next set of records.
          before (int, optional): The cursor value for fetching the previous set of records.

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """

        ps = page_size or 10
        parts = [f'page_size={ps}']

        if after is not None:
            parts.append(f'after={after}')
        if before is not None:
            parts.append(f'before={before}')

        query = '&'.join(parts)
        path = f'/history?{query}'

        return self._get(path, headers={"Accept": "application/vnd.go.cd.v1+json"})

    def release(self):
        """Releases a previously locked pipeline

        See the `Go pipeline release lock documentation`__ for example
        responses.

        .. __: http://api.go.cd/current/#releasing-a-pipeline-lock

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """
        return self._post('/unlock', headers={
            "Accept":"application/vnd.go.cd.v1+json","X-GoCD-Confirm": "True"}, method="POST")

    #: This is an alias for :meth:`release`
    unlock = release

    def pause(self, reason='Triggered via API. No reason provided.'):
        """Pauses the current pipeline

        See the `Go pipeline pause documentation`__ for example responses.

        .. __: http://api.go.cd/current/#pause-a-pipeline

        Args:
          reason (str, optional): The reason the pipeline is being paused.

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """
        return self._post('/pause', headers={
            "Accept": "application/vnd.go.cd.v1+json",
            "Content-Type": "application/json"}, pause_cause=reason)

    def unpause(self):
        """Unpauses the pipeline

        See the `Go pipeline unpause documentation`__ for example responses.

        .. __: http://api.go.cd/current/#unpause-a-pipeline

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """
        return self._post('/unpause', headers={
            "X-GoCD-Confirm": "True",
            "Accept": "application/vnd.go.cd.v1+json"}, method="POST")

    def status(self):
        """Returns the current status of this pipeline

        See the `Go pipeline status documentation`__ for example responses.

        .. __: http://api.go.cd/current/#get-pipeline-status

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """
        return self._get('/status', headers={
            "Accept": "application/vnd.go.cd.v1+json"
        })

    def instance(self, pipeline_counter=0):
        """Returns all the information regarding a specific pipeline run

        See the `Go pipeline instance documentation`__ for examples.

        .. __: https://api.gocd.org/26.1.0/#get-pipeline-instance

        Args:
          pipeline_counter (int): The pipeline instance to fetch.
            If falsey returns the latest pipeline instance from :meth:`history`.

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """

        return self._get('/{counter:d}'.format(counter=pipeline_counter), headers={
            "Accept": "application/vnd.go.cd.v1+json"
        })

    def schedule(self, variables=None, secure_variables=None, materials=None,
                 return_new_instance=False, backoff_time=1.0):
        """Schedule a pipeline run

        Aliased as :meth:`run`, :meth:`schedule`, and :meth:`trigger`.

        Args:
          variables (dict, optional): Variables to set/override
          secure_variables (dict, optional): Secure variables to set/override
          materials (dict, optional): Material revisions to be used for
            this pipeline run. The exact format for this is a bit iffy,
            have a look at the official
            `Go pipeline scheduling documentation`__ or inspect a call
            from triggering manually in the UI.
          return_new_instance (bool): Returns a :meth:`history` compatible
            response for the newly scheduled instance. This is primarily so
            users easily can get the new instance number. **Note:** This is done
            in a very naive way, it just checks that the instance number is
            higher than before the pipeline was triggered.
          backoff_time (float): How long between each check for
            :arg:`return_new_instance`.

         .. __: http://api.go.cd/current/#scheduling-pipelines

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """
        scheduling_args = dict(
            variables=variables,
            secure_variables=secure_variables,
            material_fingerprint=materials,
            headers={
                "Accept":"application/vnd.go.cd.v1+json",
                "Content-Type":"application/json",
                "X-GoCD-Confirm":"true"
            },
        )

        scheduling_args = dict((k, v) for k, v in scheduling_args.items() if v is not None)

        # TODO: Replace this with whatever is the official way as soon as gocd#990 is fixed.
        # https://github.com/gocd/gocd/issues/990
        if return_new_instance:
            pipelines = self.history()['pipelines']
            if len(pipelines) == 0:
                last_run = None
            else:
                last_run = pipelines[0]['counter']
            response = self._post('/schedule', ok_status=202, method="POST", **scheduling_args)
            if not response:
                return response

            max_tries = 10
            while max_tries > 0:
                current = self.instance()
                if not last_run and current:
                    return current
                elif last_run and current['counter'] > last_run:
                    return current
                else:
                    time.sleep(backoff_time)
                    max_tries -= 1

            # I can't come up with a scenario in testing where this would happen, but it seems
            # better than returning None.
            return response
        else:
            return self._post('/schedule', ok_status=202, method="POST", **scheduling_args)

    #: This is an alias for :meth:`schedule`
    run = schedule
    #: This is an alias for :meth:`schedule`
    trigger = schedule

    def artifact(self, counter, stage, job, stage_counter=1):
        """Helper to instantiate an :class:`gocd.api.artifact.Artifact` object

        Args:
          counter (int): The pipeline counter to get the artifact for
          stage: Stage name
          job: Job name
          stage_counter: Defaults to 1

        Returns:
          Artifact: :class:`gocd.api.artifact.Artifact` object
        """
        return Artifact(self.server, self.name, counter, stage, job, stage_counter)

    # TODO: It would be nice if this could stream the output as it happens.
    # Currently it's built with the assumption that this is done after all output has finished.
    def console_output(self, instance=None):
        """Yields the output and metadata from all jobs in the pipeline

        Args:
          instance: The result of a :meth:`instance` call, if not supplied
            the latest of the pipeline will be used.

        Yields:
          tuple: (metadata (dict), output (str)).

          metadata contains:
            - pipeline
            - pipeline_counter
            - stage
            - stage_counter
            - job
            - job_result
        """
        if instance is None:
            instance = self.instance()

        for stage in instance['stages']:
            for job in stage['jobs']:
                if job['result'] not in self.final_results:
                    continue

                artifact = self.artifact(
                    instance['counter'],
                    stage['name'],
                    job['name'],
                    stage['counter']
                )
                output = artifact.get('cruise-output/console.log')

                yield (
                    {
                        'pipeline': self.name,
                        'pipeline_counter': instance['counter'],
                        'stage': stage['name'],
                        'stage_counter': stage['counter'],
                        'job': job['name'],
                        'job_result': job['result'],
                    },
                    output.body
                )

    def stage(self, name, pipeline_counter=None):
        """Helper to instantiate a :class:`gocd.api.stage.Stage` object

        Args:
            name: The name of the stage
            pipeline_counter:

        Returns:

        """
        return Stage(
            self.server,
            pipeline_name=self.name,
            stage_name=name,
            pipeline_counter=pipeline_counter,
        )
