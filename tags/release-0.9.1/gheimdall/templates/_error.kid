<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
<head>
  <title py:content="title">Title</title>
</head>

<body>
  <div id="content">
    <h1 py:content="title"></h1>
    <p class="error"><span>${status}</span>&nbsp;<span>Error occurred.</span></p>
    <pre py:if="tg.config('server.environment') == 'development'" py:content="details">Traceback here.</pre>
  </div>
</body>
</html>
