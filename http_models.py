import logging
import time

from requests import exceptions, models

logger = logging.getLogger("messagereport")


class ScraperResponse(models.Response):
    def wait_on_429(self):
        retry_time = int(self.headers.get("Retry-After")) + 100
        logger.error(f"Waiting for: {retry_time} sec")
        time.sleep(retry_time)
        return True

    def raise_for_status(self):
        """Raises :class:`HTTPError`, if one occurred."""

        http_error_msg = ""
        if isinstance(self.reason, bytes):
            # We attempt to decode utf-8 first because some servers
            # choose to localize their reason strings. If the string
            # isn't utf-8, we fall back to iso-8859-1 for all other
            # encodings. (See PR #3538)
            try:
                reason = self.reason.decode("utf-8")
            except UnicodeDecodeError:
                reason = self.reason.decode("iso-8859-1")
        else:
            reason = self.reason

        if self.status_code == 301:
            logger.warning(f"Status Code: {self.status_code}. {self.url} redirected.")
            return True
        elif self.status_code == 500:
            logger.warning(
                f"Status Code: {self.status_code}. {self.url} Inernal server error."
            )
            return True
        elif self.status_code == 403:
            logger.warning(f"Status Code: {self.status_code}. {self.url} Forbidden")
            return True
        elif self.status_code == 429:
            return self.wait_on_429()
        elif 400 <= self.status_code < 500:
            http_error_msg = (
                f"{self.status_code} Client Error: {reason} for url: {self.url}"
            )
        elif 500 <= self.status_code < 600:
            http_error_msg = (
                f"{self.status_code} Server Error: {reason} for url: {self.url}"
            )

        if http_error_msg:
            raise exceptions.HTTPError(http_error_msg, response=self)
