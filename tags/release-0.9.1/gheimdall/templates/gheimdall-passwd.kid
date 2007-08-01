<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
<head>
  <meta content="text/html; charset=UTF-8"
        http-equiv="content-type" py:replace="''"/>
  <title>Change password</title>
</head>

<body>
  <div id="formBox">
    <h1>Change password</h1>
    <p>${values['user_name']}@${tg.config('apps.domain')}</p>
    <div py:content="form.display(values)"/>
    <form py:if="values['backURL']==''"><input type="button" id="close" name="close" py:attrs="value=_('Close')" onclick="window.close();"/></form>
    <p><a href="${values['backURL']}" py:if="values['backURL']!=''">Back</a></p>
  </div>
</body>
</html>
