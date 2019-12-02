"""
Test the stackify.__init__ setup functions
"""

import unittest
from mock import patch
from .bases import ClearEnvTest

import stackify
import logging


class TestInit(ClearEnvTest):
    '''
    Test the logger init functionality
    '''

    def setUp(self):
        super(TestInit, self).setUp()
        self.config = stackify.transport.application.ApiConfiguration(
            application='test_appname',
            environment='test_environment',
            api_key='test_apikey',
            api_url='test_apiurl')
        self.loggers = []

    def tearDown(self):
        super(TestInit, self).tearDown()
        global_loggers = logging.Logger.manager.loggerDict
        for logger in self.loggers:
            del global_loggers[logger.name]

    def test_logger_no_config(self):
        '''Logger API config loads from the environment automatically'''
        env_map = {
            'STACKIFY_APPLICATION': 'test2_appname',
            'STACKIFY_ENVIRONMENT': 'test2_environment',
            'STACKIFY_API_KEY': 'test2_apikey',
            'STACKIFY_API_URL': 'test2_apiurl',
        }

        with patch.dict('os.environ', env_map):
            logger = stackify.getLogger(auto_shutdown=False)
            self.loggers.append(logger)

        config = logger.handlers[0].listener.transport._api_config

        self.assertEqual(config.application, 'test2_appname')
        self.assertEqual(config.environment, 'test2_environment')
        self.assertEqual(config.api_key, 'test2_apikey')
        self.assertEqual(config.api_url, 'test2_apiurl')

    def test_logger_api_config(self):
        '''Logger API config loads from the specified config objects'''
        logger = stackify.getLogger(config=self.config, auto_shutdown=False)
        self.loggers.append(logger)

        config = logger.handlers[0].listener.transport._api_config

        self.assertEqual(config.application, 'test_appname')
        self.assertEqual(config.environment, 'test_environment')
        self.assertEqual(config.api_key, 'test_apikey')
        self.assertEqual(config.api_url, 'test_apiurl')

    def test_logger_name(self):
        '''The automatic logger name is the current module'''
        self.assertEqual(stackify.getCallerName(), 'tests.test_init')

    def test_get_logger_defaults(self):
        '''The logger has sane defaults'''
        env_map = {
            'STACKIFY_APPLICATION': 'test2_appname',
            'STACKIFY_ENVIRONMENT': 'test2_environment',
            'STACKIFY_API_KEY': 'test2_apikey',
        }

        with patch.dict('os.environ', env_map):
            logger = stackify.getLogger(auto_shutdown=False)
            self.loggers.append(logger)

        handler = logger.handlers[0]
        config = handler.listener.transport._api_config

        self.assertEqual(logger.name, 'tests.test_init')
        self.assertEqual(config.api_url, stackify.constants.API_URL)
        self.assertEqual(handler.listener.max_batch, stackify.constants.MAX_BATCH)
        self.assertEqual(handler.queue.maxsize, stackify.constants.QUEUE_SIZE)
        # nose will goof with the following assert
        # self.assertEqual(logger.getEffectiveLevel(), logging.WARNING)

    def test_get_logger_reuse(self):
        '''Grabbing a logger twice results in the same logger'''
        logger = stackify.getLogger(config=self.config, auto_shutdown=False)
        self.loggers.append(logger)
        logger_two = stackify.getLogger(config=self.config, auto_shutdown=False)
        self.assertIs(logger_two, logger)

    @patch('atexit.register')
    def test_logger_atexit(self, func):
        '''Logger registers an atexit function to clean up'''
        logger = stackify.getLogger(config=self.config)
        self.loggers.append(logger)
        func.assert_called_with(stackify.stopLogging, logger)

    def test_get_handlers(self):
        '''Registered handlers are provided by getHandlers'''
        logger = stackify.getLogger(config=self.config, auto_shutdown=False)
        self.loggers.append(logger)
        self.assertEqual(logger.handlers, stackify.getHandlers(logger))


if __name__ == '__main__':
    unittest.main()
