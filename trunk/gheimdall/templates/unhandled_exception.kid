<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
<head>
  <title py:content="message">Title</title>
</head>

<body>
  <h1>Oops! An error occured</h1>
  <p>Something went wonky and we weren't expecting it. Sorry about that.</p>

  <p>This is commonly known as an &quot;Error 500  &quot; or
    &quot;Internal Server Error&quot;. It means we messed up.</p>

  <p py:if="email_sent">A programmer has been notified and
    will try to fix the problem as soon as possible.</p>

  <p py:if="email_not_sent">The problem was actually so bad that
    we couldn't even send an E-mail to our team to sort the problem out!
    If you keep getting this message, please send us an E-mail with some
    information about what you were doing when this happened, so we can
    try and smooth things over :-)</p>

  <p>Our sincerest apologies,</p>

  <!--! No <em>because this is just convention !-->
  <p style="font-style: italic">-The Team</p>

</body>
</html>
