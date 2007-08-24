<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
<head>
  <meta content="text/html; charset=UTF-8"
        http-equiv="content-type" py:replace="''"/>
  <title>Your password has changed.</title>
</head>

<body>
  <div id="formBox">
    <h1>Your password has changed.</h1>
    <p>${user_name}@${tg.config('apps.domain')}</p>
    <form py:if="backURL==''"><input type="button" id="close" name="close" py:attrs="value=_('Close')" onclick="window.close();"/></form>
    <p><a href="${backURL}" py:if="backURL!=''">Back</a></p>
  </div>
</body>
</html>
