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
    * TBD
    * TBD

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
* Docker: https://www.docker.com/get-docker
* Make: https://www.gnu.org/software/make/

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
git clone --recurse-submodules TBD
```

Note: Make sure you specify the --recurse-submodules option on the clone command line. This option will cause the cloning of all dependent submodules:

### Build the Application

#### Build Process

The SDC/SDW uses Maven to manage builds

**Step 1**: Generate ASN.1 Code

For more information on this process, please see the documenation for the [PER XER Codec](per-xer-codec/README.md)

```bash
cd per-xer-codex/asn1-codegen
make directories
cp ... per-xer-codec/asn1-codegen/src/asn1/
make all install
cd ../..
```

**Step 2**: Build the maven artifacts

```bash
mvn install
```

**Step 3**: Configure docker images

Edit [build-docker-images.env](build-docker-images.env) to set the image names and versions appropriately.

**Step 4**: Build docker images

```bash
./build-docker-imges.sh
```

See the README's for each sub-project for information on configuring specific images.

#### Building docker images on non-linux systems

Building docker images on non-linux systems is not currently automated to the same
degree, due to the need to build a linux shared object file from the PER XER Codec.
If you are building and deploying natively, these steps are uncessary, but if you
intend to build docker images on anything other than linux, you will need to perform
these additional steps.

**Step 1**: Manually build PerXerCodec

After completing step 1 from the main build sequence, use make to build the shared object
inside of a docker container.

```bash
cd per-xer-codec/native
make all install
cd ../..
```

**Step 2**: Manually copy shared object

After completing step 2 from the main build sequence, copy the shared object file to the necessary directories

```bash
cp per-xer-codec/java/target/libper-xer-codec.so fedgov-cv-message-validator-webapp/target/
cp per-xer-codec/java/target/libper-xer-codec.so fedgov-cv-whtools-webapp/target/
```

From here, you can continue with step 3 of the main build sequence.

### Deploy the Application

From here, please follow the [deployment guide](https://usdotjposdcsdw.atlassian.net/wiki/spaces/SDCSDW/pages/34340865/AWS+Bootstrap+Deployment) on the wiki
