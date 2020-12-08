scriptDir=$(cd $(dirname "$0") && pwd);
scriptName=$(basename $(test -L "$0" && readlink "$0" || echo "$0"));

echo "scriptDir=$scriptDir"

projectHome=${scriptDir%/ansible-solace-collection}
if [[ ! $projectHome =~ "ansible-solace-collection" ]]; then
  echo "adding it"
  projectHome=$projectHome/ansible-solace-collection
fi


echo "projectHome=$projectHome"
