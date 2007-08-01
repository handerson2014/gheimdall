<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
<head>
  <meta content="text/html; charset=UTF-8"
        http-equiv="content-type" py:replace="''"/>
  <title>Changing password is not available here</title>
</head>

<body>
  <div id="formBox">
    <h1>Not available</h1>
    <div>${user_name}@${tg.config('apps.domain')}</div>
    <form><input type="button" id="close" name="close" py:attrs="value=_('Close')" onclick="window.close();"/></form>
  </div>
</body>
</html>
