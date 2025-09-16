
## 介绍

JSON Web 令牌 （JWT） 是一种开放标准 （[RFC 7519](https://tools.ietf.org/html/rfc7519)），它定义了一种紧凑且自包含的方式，用于将信息作为 JSON 对象在各方之间安全地传输。此信息是经过数字签名的，因此可以验证和信任。

## 使用场景

- 授权
    
- 信息交换
    

## JSON WEB令牌的结构

在其紧凑形式中，JSON Web 令牌由三个部分组成，由点 （`.）` 分隔，它们是：

- Header 页眉
    
- Payload 有效载荷
    
- Signature 签名
    

因此，JWT 通常如下所示。

xxxxx.yyyyy.zzzzz

### Header 页眉

标头_通常由_两部分组成：令牌的类型（JWT）和正在使用的签名算法，例如 HMAC SHA256 或 RSA。

{  
  "alg": "HS256",  
  "typ": "JWT"  
}

然后，此 JSON 经过 **Base64Url** 编码以形成 JWT 的第一部分。

### Payload 有效载荷

令牌的第二部分是有效负载，其中包含声明。声明是关于实体（通常是用户）和其他数据的声明。有三种类型的声明：registered， public, private claims

#### registered

这些是一组预定义的声明，不是强制性的，但建议使用，以提供一组有用的、可互操作的声明。其中一些是：**iss**（颁发者）、**exp**（过期时间）、**sub**（主题）、**aud**（受众[）等。

#### public

这些声明可以由使用 JWT 的用户随意定义。但为避免冲突，应在 [IANA JSON Web 令牌注册表](https://www.iana.org/assignments/jwt/jwt.xhtml)中定义它们，或将其定义为包含抗冲突命名空间的 URI。

#### private claims

这些是自定义声明，用于在同意使用它们的各方之间共享信息，既不是_注册_声明，也不是_公开_声明。

一个示例有效负载可以是：

{  
  "sub": "1234567890",  
  "name": "John Doe",  
  "admin": true  
}

然后，对有效负载进行 **Base64Url** 编码，以形成 JSON Web 令牌的第二部分。

### Signature 签名

要创建签名部分，您必须获取编码的标头、编码的有效负载、密钥、标头中指定的算法，并对其进行签名。

例如，如果您想使用 HMAC SHA256 算法，将按以下方式创建签名：

HMACSHA256(  
  base64UrlEncode(header) + "." +  
  base64UrlEncode(payload),  
  secret)

签名用于验证消息在整个过程中没有被更改，并且在使用私钥签名的令牌的情况下，它还可以验证 JWT 的发件人是否是它所声称的身份。

## jwt作用

jwt的设计理念是通过签名提供数据的完整性和身份验证，jwt token的头部和负载部分是明文传输的，是通过base64url统一编码后的字符串，而签名部分是使用特定的算法对 base64编码后的头部和负载 + 密匙 进行加密获得的字符串，所以这部分可以保证信息的完整性和身份验证，因为只有通过获得相同的算法和密匙才能够获得相同的签名 字符串