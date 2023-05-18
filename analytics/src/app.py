from raya.application_base import RayaApplicationBase
from raya.controllers.analytics_controller import AnalyticsController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.analytics:AnalyticsController = \
                await self.enable_controller('analytics')


    async def loop(self):
        self.log.info('starter analytics log')
        await self.analytics.track(
                event_name='button clicked', 
                parameters={'origin': 'main_page'}
            )


    async def finish(self):
        self.log.info((
                'App finished - check directory '
                '\'/opt/raya_os/data/Mixpanel-analytics\''
            ))
