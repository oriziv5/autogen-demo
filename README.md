# Autogen demo

In  this code snippet you will learn how to use `autogen` to create multi agent workflow using Azure Open AI


## Environment Prerequisites
1. Install docker client [here](https://docs.docker.com/desktop/)
2. Install `ms-vscode-remote.remote-containers` extension in vscode
3. Run devcontainer.json (build and open remote), this will prepare your dev environment with all nesessary dependencies


## Application prerequisites
1. [Create new](https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesOpenAI) `Azure Open AI` resource at azure portal
2. Select "East US" and Standard S0 tier
3. When resource is created add role "Cognitive Services OpenAI Contributor" to your user.
4. In the main blade of the resouces go to "Azure AI portal"
5. Click "Create new deployment" -> From base models
6. Select `gpt-4o`
7. Deploy the model (Standard)
8. Create `.env` file with 
    ```
    AZURE_OPENAI_ENDPOINT=<ENDPOINT VALUE>
    AZURE_OPENAI_MODEL=gpt-4o
    AZURE_OPENAI_API_VERSION=2024-02-15-preview
    ```
8. Click "View Code" and copy the `ENDPOINT` value into above field.
9. login to azure using `az login` and select the subscription you want
10. run the program ```python3 main.py```