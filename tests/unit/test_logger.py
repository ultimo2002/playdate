from src.algoritmes.logger import *
from tests.unit.unit_helpers import *

import logging
import sys
from collections import deque


class TestLoggingSetup(unittest.TestCase):
    def setUp(self):
        # Reset the global log buffer before each test
        global LOG_BUFFER
        LOG_BUFFER.clear()

        # Capture the logs in a string buffer
        self.log_capture = deque(maxlen=MAX_LOG_BUFFER_SIZE)

        # Custom handler for capturing logs
        class TestHandler(logging.Handler):
            def emit(inner_self, record):
                self.log_capture.append(inner_self.format(record))

        # Attach test handler
        self.test_handler = TestHandler()
        self.test_handler.setLevel(logging.DEBUG)
        self.test_handler.setFormatter(formatter)
        logger.addHandler(self.test_handler)

    def tearDown(self):
        # Remove the test handler after each test
        logger.removeHandler(self.test_handler)

    def test_logging_levels(self):
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

        # Ensure logs are captured in order
        self.assertIn("Warning message", self.log_capture[-3])
        self.assertIn("Error message", self.log_capture[-2])
        self.assertIn("Critical message", self.log_capture[-1])

    def test_log_buffer_max_size(self):
        # Fill the buffer beyond its max size
        for i in range(MAX_LOG_BUFFER_SIZE + 10):
            logger.warning(f"Message {i}")

        # Ensure the buffer size does not exceed max size
        self.assertEqual(len(LOG_BUFFER), MAX_LOG_BUFFER_SIZE)
        self.assertIn(f"Message {10}", LOG_BUFFER[0])  # Oldest message should be removed

    def test_stream_interceptor(self):
        # Capture stdout output
        original_stdout = sys.stdout
        sys.stdout = StreamInterceptor(original_stdout)

        print("Intercepted print statement")

        sys.stdout = original_stdout  # Restore stdout

        self.assertTrue(any("Intercepted print statement" in msg for msg in LOG_BUFFER))
