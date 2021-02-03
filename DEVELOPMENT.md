# Development

At the moment, this project is hosted in both `CodeCommit` and `Gitlab`.

In order to setup both remotes to your Git please do the following:

In case you already have an `origin` defined
```
git remote remove origin
```

for fetch:
```
git remote add origin codecommit::us-east-1://aws-auto-inventory
````

for push:
```
git remote set-url origin --push --add codecommit::us-east-1://aws-auto-inventory
git remote set-url origin --push --add git@ssh.gitlab.aws.dev:proserve-solutions/aws-auto-inventory.git
```

check your origin now
```
git remote -v
origin	codecommit::us-east-1://aws-auto-inventory (fetch)
origin	codecommit::us-east-1://aws-auto-inventory (push)
origin	git@ssh.gitlab.aws.dev:proserve-solutions/aws-auto-inventory.git (push)

git push -u origin master
Branch 'master' set up to track remote branch 'master' from 'origin'.
Everything up-to-date
Branch 'master' set up to track remote branch 'master' from 'origin'.
Everything up-to-date
```

