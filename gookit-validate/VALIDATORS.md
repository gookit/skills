# 内置验证器

## 必填验证

| 验证器 | 说明 |
|--------|------|
| `required` | 字段必填，不能为空 |
| `required_if:field,val,...` | 当指定字段等于某值时必填 |
| `required_unless:field,val,...` | 除非指定字段等于某值，否则必填 |
| `required_with:field1,field2` | 任一指定字段存在时必填 |
| `required_with_all:field1,field2` | 所有指定字段都存在时必填 |
| `required_without:field1,field2` | 任一指定字段不存在时必填 |
| `required_without_all:field1,field2` | 所有指定字段都不存在时必填 |
| `-` / `safe` | 跳过该字段验证 |

## 类型验证

| 验证器 | 说明 |
|--------|------|
| `int` / `integer` | 整型 (intX, uintX)，可带范围 `int:2,12` |
| `uint` | 无符号整型 |
| `bool` / `isBool` | 布尔值 ("1","on","yes","true" → true) |
| `string` / `isString` | 字符串 |
| `float` / `isFloat` | 浮点型 |
| `slice` / `isSlice` | 切片类型 |

## 长度验证

| 验证器 | 说明 |
|--------|------|
| `len:N` | 长度等于 N |
| `minLen:N` / `minLength:N` | 最小长度 N |
| `maxLen:N` / `maxLength:N` | 最大长度 N |

## 范围验证

| 验证器 | 说明 |
|--------|------|
| `min:N` | 最小值 (数字类型) |
| `max:N` | 最大值 (数字类型) |
| `range:N1,N2` / `between:N1,N2` | 范围 [N1, N2] |

## 字符串包含

| 验证器 | 说明 |
|--------|------|
| `contains:value` | 包含指定值 |
| `not_contains:value` | 不包含指定值 |
| `starts_with:value` | 开头匹配 |
| `ends_with:value` | 结尾匹配 |

## 枚举验证

| 验证器 | 说明 |
|--------|------|
| `in:a,b,c` | 值在枚举中 |
| `not_in:value` | 值不在枚举中 |

## 相等验证

| 验证器 | 说明 |
|--------|------|
| `eq:value` / `equal` | 等于指定值 |
| `ne:value` / `notEqual` | 不等于指定值 |
| `lt:value` / `lessThan` | 小于 (数字) |
| `gt:value` / `greaterThan` | 大于 (数字) |
| `lte:value` | 小于等于 |
| `gte:value` | 大于等于 |
| `eq_field:field` | 等于另一字段 |
| `ne_field:field` | 不等于另一字段 |
| `gt_field:field` | 大于另一字段 |
| `gte_field:field` | 大于等于另一字段 |
| `lt_field:field` | 小于另一字段 |
| `lte_field:field` | 小于等于另一字段 |

## 格式验证

| 验证器 | 说明 |
|--------|------|
| `email` | 邮箱格式 |
| `regex:pattern` | 正则匹配 |
| `date` | 日期格式 `2018-10-25` |
| `gt_date:value` | 大于指定日期 |
| `lt_date:value` | 小于指定日期 |
| `gte_date:value` | 大于等于指定日期 |
| `lte_date:value` | 小于等于指定日期 |

## URL/IP

| 验证器 | 说明 |
|--------|------|
| `url` | URL 格式 |
| `fullUrl` | 完整 URL (必须 http/https 开头) |
| `ip` | IP 地址 (v4/v6) |
| `ipv4` | IPv4 |
| `ipv6` | IPv6 |
| `CIDR` | CIDR 格式 |
| `MAC` | MAC 地址 |

## 字符串类型

| 验证器 | 说明 |
|--------|------|
| `alpha` | 只含字母 |
| `alphaNum` | 只含字母和数字 |
| `alphaDash` | 字母、数字、中划线、下划线 |
| `ascii` | ASCII 字符 |
| `base64` | Base64 编码 |
| `hex` / `hexadecimal` | 十六进制 |
| `json` | JSON 格式 |
| `printableASCII` | 可打印 ASCII |
| `multiByte` | 多字节字符串 |

## 特殊格式

| 验证器 | 说明 |
|--------|------|
| `cn_mobile` | 中国手机号 |
| `isbn10` | ISBN-10 |
| `isbn13` | ISBN-13 |
| `uuid` | UUID |
| `uuid3` / `uuid4` / `uuid5` | 指定版本 UUID |
| `hexColor` | 十六进制颜色 |
| `rgbColor` | RGB 颜色 |
| `dnsName` | DNS 名称 |
| `dataURI` | Data URI |

## 文件上传

| 验证器 | 说明 |
|--------|------|
| `file` | 上传文件 |
| `image` | 图片文件 (支持后缀检查) |
| `mime:type1,type2` | 指定 MIME 类型 |
| `filePath` | 存在的文件路径 |
| `unixPath` | Unix 路径 |
| `winPath` | Windows 路径 |

## 地理位置

| 验证器 | 说明 |
|--------|------|
| `lat` / `latitude` | 纬度 |
| `lon` / `longitude` | 经度 |
