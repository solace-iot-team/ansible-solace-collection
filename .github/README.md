# Github Workflows

## Generate Azure Service Principal

[See: Generate the Service Principal](https://docs.microsoft.com/en-gb/cli/azure/ad/sp?view=azure-cli-latest#az_ad_sp_create_for_rbac).


````bash
az ad sp create-for-rbac --name "solace-int-rdp-az-funcs" --sdk-auth

# make a note of the output, similar to this:
{
  "clientId": "{client-id}",
  "clientSecret": "{client-secret}",
  "subscriptionId": "{subscription-id}",
  "tenantId": "{tenant-id}",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}

````

## Github Secrets

- **AZURE_CREDENTIALS** = {copy service principal output}
- **ANSIBLE_GALAXY_TOKEN**
- **SOLACE_CLOUD_API_TOKEN_ALL_PERMISSIONS**
- **SOLACE_CLOUD_API_TOKEN_RESTRICTED_PERMISSIONS**



---
