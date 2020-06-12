import logging
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from pathlib import Path

from .action import Action

logger = logging.getLogger(__name__)


class Email(Action):
    def __init__(
        self,
        send_from,
        send_to,
        subject,
        message,
        server="localhost",
        port=587,
        username="",
        password="",
        use_tls=True,
    ) -> None:
        """Compose and send email with provided info and attachments.

        Args:
            send_from (str): from name
            send_to (list[str]): to name(s)
            subject (str): message title
            message (str): message body
            server (str): mail server host name
            port (int): port number
            username (str): server auth username
            password (str): server auth password
            use_tls (bool): use TLS mode
        """
        self.send_from = send_from
        self.send_to = send_to
        self.subject = subject
        self.message = message
        self.server = server
        self.port = port
        self.username = username or send_from
        self.password = password
        self.use_tls = use_tls

    def pipeline(self, args) -> None:
        path = args["path"]
        simulate = args["simulate"]

        full_subject = self.fill_template_tags(self.subject, args)
        full_message = self.fill_template_tags(self.message, args)
        self.print(
            "\nRecp: %s\nSubj: %s\n%s"
            % (", ".join(self.send_to), full_subject, full_message)
        )
        if not simulate:
            msg = MIMEMultipart()
            msg["From"] = self.send_from
            msg["To"] = COMMASPACE.join(self.send_to)
            msg["Date"] = formatdate(localtime=True)
            msg["Subject"] = full_subject

            msg.attach(MIMEText(full_message))

            part = MIMEBase("application", "octet-stream")
            with open(path, "rb") as f:
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition", 'attachment; filename="{}"'.format(Path(path).name)
            )
            msg.attach(part)

            smtp = smtplib.SMTP(self.server, self.port)
            if self.use_tls:
                smtp.starttls()
            smtp.login(self.username, self.password)
            smtp.sendmail(self.send_from, self.send_to, msg.as_string())
            smtp.quit()

    def __str__(self) -> str:
        return "Email"
