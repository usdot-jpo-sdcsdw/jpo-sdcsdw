# jpo-sdcsdw
US Department of Transportation Joint Program office (JPO) Situational Data Clearinghouse/Situational Data Warehouse (SDC/SDW)

In the context of ITS, the Situation Data Warehouse is a software system that
allows users to deposit situational data for use with connected vehicles (CV) and
later query for that data.

![Diagram](doc/images/mvp-architecture-diagram.png)

<a name="toc"/>

## Table of Contents

[I. Release Notes](#release-notes)

[II. Documentation](#documentation)

[III. Collaboration Tools](#collaboration-tools)

[IV. Getting Started](#getting-started)

---

<a name="release-notes"/>

## [I. Release Notes](ReleaseNotes.md)

<a name="documentation"/>

## II. Documentation

<a name="collaboration-tools"/>

## III. Collaboration Tools

### Source Repositories - GitHub

* Main repository on GitHub (public)
    * https://github.com/usdot-jpo-sdcsdw/jpo-sdcsdw
    * git@github.com:usdot-jpo-sdcsdw/jpo-sdcsdw.git

### Agile Project Managment - Jira

https://usdotjposdcsdw.atlassian.net/secure/RapidBoard.jspa?rapidView=1&projectKey=SDCSDW

### Wiki - Confluence

https://usdotjposdcsdw.atlassian.net/wiki/spaces/SDCSDW/overview

### Continuous Integration and Delivery

TODO

### Static Code Analysis

TODO

<a name="getting-started"/>

## IV. Getting Started

The following instructions describe the procedure to fetch, build, and run the application.

### Prerequisites

* JDK 1.8: http://www.oracle.com/technetwork/pt/java/javase/downloads/jdk8-downloads-2133151.html
* Maven: https://maven.apache.org/install.html
* Git: https://git-scm.com/
* OpenSSL: https://www.openssl.org/ (If creating self-signed certificates)
* Docker: https://www.docker.com/get-docker
* Make: https://www.gnu.org/software/make/
* Autotools: https://www.gnu.org/software/automake/manual/html_node/index.html#Top
* Clang: https://clang.llvm.org/ (MacOS, Linux)
* GCC: http://gcc.gnu.org/ (Windows)
* Docker: https://www.docker.com/get-started
    * Optional if building on MacOS or Linux and not planning on deploying the system in Docker
* Kubectl: https://kubernetes.io/docs/tasks/tools/install-kubectl/ (If deploying)
* Helm: https://docs.helm.sh/using_helm/ (If deploying)
* Minikube: https://kubernetes.io/docs/setup/minikube/ (If deploying locally on linux)


---

### Obtain the Source Code

|Name|Description|
|----|-----------|
|[common-models](https://github.com/usdot-jpo-sdcsdw/common-models)|Models containing traveler information|
|[per-xer-codec](https://github.com/usdot-jpo-sdcsdw/per-xer-codec)|JNI Wrapper around asn1c-generated code|
|[udp-interface](https://github.com/usdot-jpo-sdcsdw/udp-interface)|Interface for querying traveler information over UDP using the SEMI extensions protocol|
|[fedgov-cv-webapp-websocket](https://github.com/usdot-jpo-sdcsdw/fedgov-cv-webapp-websocket)|Interface for depositing and querying for traveler information over Websockets|
|[fedgov-cv-whtools-webapp](https://github.com/usdot-jpo-sdcsdw/fedgov-cv-whtools-webapp)|Web GUI front-end for the websockets interface|
|[fedgov-cv-sso-webapp](https://github.com/usdot-jpo-sdcsdw/fedgov-cv-sso-webapp)|Central Authentication Server for securing the Web GUI and Websockets back-end|
|[credentials-db](https://github.com/usdot-jpo-sdcsdw/credentials-db)|Docker image for storing user credentials|
|[fedgov-cv-message-validator-webapp](https://github.com/usdot-jpo-sdcsdw/fedgov-cv-message-validator-webapp)|Web GUI for validating messages to be deposited|
|[tim-db](https://github.com/usdot-jpo-sdcsdw/tim-db)|Docker image for storing traveler information|


#### Step 1 - Clone public repository

Clone the source code from the GitHub Repository using Git Command:

```bash
git clone --recurse-submodules https://github.com/usdot-jpo-sdcsdw/jpo-sdcsdw
```

Note: Make sure you specify the --recurse-submodules option on the clone command line. This option will cause the cloning of all dependent submodules:

### Build the Application

NOTE: Due to [limitations in Windows](https://support.microsoft.com/en-us/help/830473/command-prompt-cmd-exe-command-line-string-limitation),
the system cannot be built normally on Windows, and cannot run on Windows. See
the section on "build.with.docker" for an explanation the impact on the build
process, and how to build non-Windows versions of system while still on Windows.

#### Build Process

The SDC/SDW uses Maven to manage builds

**Step 1**: Add ASN.1 Specification files

For more information on this process, please see the documenation for the [PER XER Codec](per-xer-codec/README.md)

```bash
cp ... per-xer-codec/asn1-codegen/src/asn1/
```

**Step 2**: Build using maven

```bash
mvn install [-Dparameter=value]...
```

##### Optional Build Parameters

These properties can be provided to control the build process:

###### build.with.docker

```bash
-Dbuild.with.docker=true
-Dbuild.with.docker=cygwin
```

Set this property to any string to enable building the artifacts (as well as
generate and build the ASN.1 codec) within a docker container. This requires
a running docker daemon as well as an install docker client configured to use
that daemon.

On windows, if you are running under a linux-like shell, such as cygwin, mingw,
git-bash, etc, set this property to "cygwin", otherwise you will experience odd
errors.

Note that unless are you running under a linux OS, the produced ASN.1 codec
binary will not be usable on your local system, and will only be runnable under
linux or another docker container.

**NOTE**: Due to the command length limitation of the windows command shell, it is
currently impossible to build the system natively on windows. You must use this
property if you are building the system on a non-posix system. This also means
that unit tests will be unable to execute during the build, to prevent this from
failing the build, add the `-Dmaven.test.skip=true` argument.

###### cygwin.install.root

```bash
-Dcygwin.install.root=C:\Path\To\Cygwin\
```

When building on windows using cygwin/mingw/git-bash, etc, by default, the build
system assumes your installation root is `C:\Program Files\Git`. Set this
property to specify a different root path.


###### per-xer-codec.skipAutogen

```bash
-Dper-xer-codec.skipAutogen=true
```

Set this property to "true" to skip re-generating the ASN.1 codec C code. If you'
have not already generated this code, this will cause the build to fail with
unexpected error messages.

###### sdcsdw.skipDocker

```bash
-Dsdcsdw.skipDocker=true
```

By default, the build system will build the five docker images for the system.
If you do not have a docker daemon accessible, or simply wish to skip this step,
set this property to "true".

Note that the docker images require a linux binary artifact from the
per-xer-codec, if you are building on Windows or MacOS in a non-docker mode,
this will cause the build to fail if you have not previously built this
artifact.

###### sdcsdw.docker.repository

```bash
-Dsdcsdw.docker.repository=my-custom-docker-repo.com:8080/
```

This property allows you to add a prefix to the docker image repository, for
example, to specify a remote URL (such as Amazon ECR). By default, this
property is blank, meaning that the image will be restricted to daemon it is
built on.

###### sdcsdw.docker.tag
```bash
-Dsdcsdw.docker.tag=1.2.3-SNAPSHOT
```

Set this property to specify the tag of the docker images. By default, this is
set to "testing" to prevent accidental overwriting or collision.

See the README's for each sub-project for information on configuring specific images.

##### Note for building docker containers behind a HTTP proxy

If you are building the system's docker containers while having your HTTP_PROXY
and related variables set, you may encounter an error similar to the following:

```bash
Jan 28, 2019 1:27:26 PM com.spotify.docker.client.shaded.org.apache.http.impl.execchain.RetryExec execute
INFO: I/O exception (com.spotify.docker.client.shaded.org.apache.http.NoHttpResponseException) caught when processing request to {}->http://proxy-east.aero.org:8080->unix://localhost:80: The target server failed to respond
```

To solve this, add the `-Ddockerfile.useProxy=false` argument.

### Deploy the Application on Kubernetes

**Step 0**: Deploy Cluster

The SDC/SDW is designed to run on Kubernetes, you will need to have access to a
kubernetes cluster with tiller (helm) installed.

If you wish to deploy locally, you may use minikube, or the built-in kubernetes
cluster in docker-for-mac and docker-for-windows.

**Step 1**: Configure Services

To configure the SDC/SDW for deployment, edit (or copy) the file at `helm/values.yaml`.

#### Configuration Values

##### use\_load\_balancer

Set to true to deploy services using load balancers. Support depends on your
cluster's configuration, however Minikube will not support this.

##### credentials\_db.image

Docker image to use for the credentials database.

##### credentials\_db.tag

Tag for docker image to use for the credentials database.

##### credentials\_db.storage\_class\_name

Name of the storage class to use to provision the persistent volume for the
credentials database.

##### credentials\_db.db\_name

Name of the database to store user credentials in.

##### credentials\_db.username

Username to connect to the credentials database.

##### credentials\_db.password\_secret.name

Name of the secret storing the password to connect to the database with.

##### credentials\_db.password\_secret.key

Key in the secret containing the password to connect to the database with.

##### credentials\_db.port.mysql

Port to connect to the credentials database with internally.

##### cas.image

Docker image to use for the central authentication server.

##### cas.tag

Tag for docker image to use for the central authentication server.

##### cas.hostname

Hostname users will connect to the central authentication server at. For
minikube, this will be the minikube's ip. For a deployed cluster, this will be
the domain name you have registered.

##### cas.port.http

Port users will connect to the central authentication server on for HTTP.
For minikube, this will need to be a unique, available NodePort.

##### cas.port.http

Port users will connect to the central authentication server on for HTTPS.
For minikube, this will need to be a unique, available NodePort.

##### message\_validator.image

Docker image to use for the message validator webapp.

##### message\_validator.tag

Tag for docker image to use for the message validator webapp.

##### message\_validator.hostname

Hostname users will connect to the message validator webapp at. For
minikube, this will be the minikube's ip. For a deployed cluster, this will be
the domain name you have registered.

##### message\_validator.port.http

Port users will connect to the message validator webapp on for HTTP.
For minikube, this will need to be a unique, available NodePort.

##### message\_validator.port.http

The port users will connect to the message validator webapp on for HTTPS
For minikube, this will need to be a unique, available NodePort.

##### tim\_db.image

Docker image to use for the TIM database.

##### tim\_db.tag

Tag for docker image to use for the TIM database.

##### credentials\_db.storage\_class\_name

Name of the storage class to use to provision the persistent volume for the
TIM database.

##### tim\_db.db\_name

Name of the database to store TIMs in.

##### tim\_db.collection\_name

Name of the collection to store TIMs in.

##### tim\_db.port.mongodb

Port to connect to the TIM database with internally.

##### whtools.image

Docker image to use for the warehouse tools webapp.

##### whtools.tag

Tag for docker image to use for the warehouse tools webapp.

##### whtools.system\_name

This is an artifact from the legacy system. The value of this field will be the
value of the "systemName" field in a request to the warehouse tools
websockets/REST interface.

##### whtools.hostname

Hostname users will connect to the warehouse tools webapp at. For
minikube, this will be the minikube's ip. For a deployed cluster, this will be
the domain name you have registered.

##### whtools.port.http

Port users will connect to the warehouse tools webapp on for HTTP.
For minikube, this will need to be a unique, available NodePort.

##### whtools.port.http

Port users will connect to the warehouse tools webapp on for HTTPS
For minikube, this will need to be a unique, available NodePort.

##### ssl.jetty\_keystore\_secret.name

Name of the secret containing the SSL/TLS certificates in JKS format.

##### ssl.jetty\_keystore\_secret.key

Key in the secret containing the SSL/TLS certificates in JKS format.

##### ssl.jetty\_keystore\_password\_secret.name

Name of the secret containing the password for the SSL/TLS certificates in JKS format.

##### ssl.jetty\_keystore\_password\_secret.key

Key in the secret containing the password for the SSL/TLS certificates in JKS format.

##### ssl.trust\_keystore

Set to true to have the warehouse tools manually trust its own SSL/TLS
certificates.
This is necessary if you are using self-signed certificates, or your root CA is
not part of the default java trust store.


**Step 2** Configure Secrets

The SDC/SDW makes use of three kubernetes-managed secrets:
* Java Keystore (JKS) containing SSL/TLS certificates
* Password to SSL/TLS certificate keystore
* Password for accessing the credentials database

If you have secrets for these values already, edit the `helm/values.yaml` file
to specify the names and keys of these secrets in the appropriate fields.

If you need to create these secrets, you may do so by hand using kubectl, but
a convenience python script `./create-secrets.py` is provided which will
examine your `helm/values.yaml` file and create the secrets appropriately. See
the usage message for `./create-secrets.py` for more information.

If you need to create a self-signed certificate keystore, see [This Document](doc/ssl.md) for
instructions.

**Step 3** Deploy with Helm

Decide on a name (&lt;name&gt;) for your deployment, optionally a namespace
(&lt;namespace&gt;) to deploy it in. If you opted to create a new values.yaml file
instead of editing the existing one, you will need to provide the path to that
file (&lt;path/to/values.yaml&gt;). When you are ready, execute the following command:

```bash
helm install --name <name> [--namespace=<namespace>] [-f <path/to/values.yaml>] helm/
```

### Update the Deployment

If you need to update your deployment, for example, upgrading a component to a
new container version, edit your `values.yaml` file once more, then execute the
following command:

```bash
helm upgrade <name> [--namespace=<namespace>] [-f <path/to/values.yaml>] helm/
```
