<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
<head>
  <meta content="text/html; charset=UTF-8"
        http-equiv="content-type" py:replace="''"/>
  <title>Logging in...</title>
</head>
<body onLoad="javascript:document.acsForm.submit()">
  <font size="+1">Please wait a second...</font>
  <form name="acsForm" py:attrs="action=acsURL" method="post">
    <div style="display: none">
      <textarea rows="10" cols="80" name="SAMLResponse">${SAMLResponse}</textarea>
      <textarea rows="10" cols="80" name="RelayState" py:content="RelayState"></textarea>
      <input type="submit" value="login"/>
    </div>
  </form>
</body>
</html>
