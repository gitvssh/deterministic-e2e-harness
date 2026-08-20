POST {{base_url}}/users
Content-Type: application/json
```
{
  "external_id": "candidate-{{run_id}}",
  "email": "candidate-{{run_id}}@example.com"
}
```
HTTP 201
[Captures]
user_id: jsonpath "$.user_id"
[Asserts]
jsonpath "$.status" == "active"

POST {{base_url}}/payments
Content-Type: application/json
```
{
  "user_id": "{{user_id}}",
  "order_id": "order-{{run_id}}",
  "amount": 12500,
  "payment_token": "synthetic-decline"
}
```
HTTP 402
[Asserts]
jsonpath "$.code" == "PAYMENT_DECLINED"
jsonpath "$.retryable" == true

POST {{base_url}}/payments/retry
Content-Type: application/json
```
{
  "user_id": "{{user_id}}",
  "order_id": "order-{{run_id}}",
  "amount": 12500,
  "payment_token": "synthetic-approve"
}
```
HTTP 200
[Captures]
payment_id: jsonpath "$.payment_id"
[Asserts]
jsonpath "$.status" == "captured"
jsonpath "$.amount" == 12500

GET {{base_url}}/payments/{{payment_id}}
HTTP 200
[Asserts]
jsonpath "$.payment_id" == "{{payment_id}}"
jsonpath "$.order_id" == "order-{{run_id}}"
jsonpath "$.status" == "captured"
jsonpath "$.amount" == 12500
