gcloud config configurations activate njit-advising

if [ -z "$1" ]
then
	gcloud app deploy -v `date +%Y-%m-%d`
else
	gcloud app deploy -v $1 --no-promote
fi
