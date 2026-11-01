# 🚀 Inicializando o Cluster - ToggleMaster

Este guia descreve os passos necessários para autenticar no cluster EKS, injetar as credenciais sensíveis via AWS Secrets Manager (utilizando o AWS CloudShell) e realizar o deploy da aplicação.

## 📋 Pré-requisitos e Configuração Inicial

Antes de executar os comandos, certifique-se de que:
1. O cluster **AWS EKS** e a infraestrutura necessária já foram provisionados.
2. Você clonou este repositório e navegou até o diretório `k8s`, onde estão os manifestos.
3. O arquivo `k8s/configmap.yaml` foi editado com os dados correspondentes ao seu ambiente em nuvem.
4. As chaves de acesso e variáveis de ambiente já foram cadastradas no **AWS Secrets Manager**.
5. Você está executando os comandos no **AWS CloudShell** (ou em um terminal autenticado na AWS) configurado para a região `us-east-1`.

---

## 🔐 1. Autenticação no Cluster

O primeiro passo é configurar o seu `kubeconfig` local para permitir a comunicação com o cluster EKS recém-criado.

```bash
aws eks update-kubeconfig --region us-east-1 --name togglemaster

```

---

## 🏗️ 2. Deploy e Injeção de Secrets

Os comandos abaixo criam o namespace da aplicação e extraem os valores do AWS Secrets Manager, injetando-os diretamente no Kubernetes de forma segura.

### Criar o Namespace

```bash
kubectl create namespace togglemaster --dry-run=client -o yaml | kubectl apply -f -

```

### Injetar Secret de Autenticação (Auth Service)

```bash
kubectl create secret generic auth-secrets \
  -n togglemaster \
  --from-literal=DATABASE_URL="$(aws secretsmanager get-secret-value --secret-id 'auth-service-secret' --region us-east-1 --query 'SecretString' --output text | jq -r .DATABASE_URL)" \
  --from-literal=MASTER_KEY="$(aws secretsmanager get-secret-value --secret-id 'auth-service-secret' --region us-east-1 --query 'SecretString' --output text | jq -r .MASTER_KEY)" \
  --dry-run=client -o yaml | kubectl apply -f -

```

### Injetar Secret de Flags (Flag Service)

```bash
kubectl create secret generic flag-secrets \
  -n togglemaster \
  --from-literal=DATABASE_URL="$(aws secretsmanager get-secret-value --secret-id 'flag-service-secret' --region us-east-1 --query 'SecretString' --output text | jq -r .DATABASE_URL)" \
  --dry-run=client -o yaml | kubectl apply -f -

```

### Injetar Secret de Targeting

```bash
kubectl create secret generic targeting-secrets \
  -n togglemaster \
  --from-literal=DATABASE_URL="$(aws secretsmanager get-secret-value --secret-id 'targeting-service-secret' --region us-east-1 --query 'SecretString' --output text | jq -r .DATABASE_URL)" \
  --dry-run=client -o yaml | kubectl apply -f -

```

### Injetar Secret de Evaluation

> ⚠️ **Atenção:** Gere a Chave de API previamente e substitua `COLE_A_CHAVE_GERADA_AQUI` no comando abaixo.

```bash
kubectl create secret generic evaluation-secrets \
  -n togglemaster \
  --from-literal=SERVICE_API_KEY="COLE_A_CHAVE_GERADA_AQUI" \
  --from-literal=REDIS_URL="$(aws secretsmanager get-secret-value --secret-id 'evaluation-secret-service' --region us-east-1 --query 'SecretString' --output text | jq -r .REDIS_URL)" \
  --dry-run=client -o yaml | kubectl apply -f -

```

### Injetar Secret de Analytics

> ⚠️ **Atenção:** As credenciais no lab da AWS academy expiram assim que o tempo lá no lab acabar e devem ser reprovisionadas.

```bash
kubectl create secret generic analytics-secrets \
  -n togglemaster \
  --from-literal=AWS_ACCESS_KEY_ID="$(aws secretsmanager get-secret-value --secret-id 'analytics-service-secret' --region us-east-1 --query 'SecretString' --output text | jq -r .AWS_ACCESS_KEY_ID)" \
  --from-literal=AWS_SECRET_ACCESS_KEY="$(aws secretsmanager get-secret-value --secret-id 'analytics-service-secret' --region us-east-1 --query 'SecretString' --output text | jq -r .AWS_SECRET_ACCESS_KEY)" \
  --from-literal=AWS_SESSION_TOKEN="$(aws secretsmanager get-secret-value --secret-id 'analytics-service-secret' --region us-east-1 --query 'SecretString' --output text | jq -r .AWS_SESSION_TOKEN)" \
  --dry-run=client -o yaml | kubectl apply -f -

```

---

## 🚀 3. Aplicar os Manifestos

Com o cluster autenticado e todos os secrets criados, aplique as configurações do projeto via Kustomize:

```bash
kubectl apply -k .

```

---

## 🌐 4. Acesso e Validação

Após a execução do deploy, obtenha o endereço externo gerado pelo balanceador de carga para testar a aplicação.

**Obter o IP Externo / DNS do LoadBalancer:**

```bash
kubectl get svc -n ingress-nginx

```

*(Copie o valor da coluna `EXTERNAL-IP` gerado pelo NGINX Ingress Controller)*

---

## 🧪 Comandos para Testar a Aplicação

*(Adicione aqui os `curl` ou instruções de acesso via navegador para validar os endpoints da sua aplicação após o deploy.)*

```

