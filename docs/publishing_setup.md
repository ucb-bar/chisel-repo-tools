# Publishing Setup
## sbt
Do you have `sbt` installed. If not start with [Installing sbt](https://www.scala-sbt.org/1.x/docs/Setup.html)

Once you have sbt installed, it is currently necessary to have the following global setting done
in `~/.sbt/1.0/plugins` add the following line to the beginning of the `plugins.sbt` file
```scala
addSbtPlugin("com.jsuereth" % "sbt-pgp" % "2.0.1")
```
This line is may be unnecessary in the future but it avoids issues that return errors like one of
```
[error] Caused by: java.lang.ClassNotFoundException: com.typesafe.sbt.SbtPgp$
[error] java.lang.NoClassDefFoundError: com/jsuereth/sbtpgp/SbtPgp$autoImport$
```

## Credentials

Sonatype requires credentials to be available in the publishing steps.

To create credentials follow the steps outlined here in
[GPG github actions recipe](https://github.com/olafurpg/sbt-ci-release#gpg)
> TIL: `pbcopy` and `xclip` are commands that copy their standard input to the system's paste buffer.
> Knowing that helps make the instructions there a bit easier to understand

## Github API

For some of the scripts you will need to have a GITHUB token.
See [Generating a github token](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token)
One way to use this token is to locally set and environment variable with this token.

```
export GHRPAT=<githubtoken>
```


 
