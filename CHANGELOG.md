# Changelog

## [1.1.1](https://github.com/aws-samples/aws-auto-inventory/compare/v1.1.0...v1.1.1) (2023-08-28)


### Bug Fixes

* log incorrect directory name ([a28cec7](https://github.com/aws-samples/aws-auto-inventory/commit/a28cec783ba51f4aa7c0604c01eb47fc1f9a21bc))

## [1.1.0](https://github.com/aws-samples/aws-auto-inventory/compare/v1.0.0...v1.1.0) (2023-08-03)


### Features

* get json from URL ([114fdf9](https://github.com/aws-samples/aws-auto-inventory/commit/114fdf9e78e76b202e43351051aa9bf2099ecf4b))

## [1.0.0](https://github.com/aws-samples/aws-auto-inventory/compare/v0.7.0...v1.0.0) (2023-08-03)


### ⚠ BREAKING CHANGES

* cleanup
* simplify business logic

### Features

* add argument max retry and retry delay ([5a15d5b](https://github.com/aws-samples/aws-auto-inventory/commit/5a15d5b5d426cf187d9a98c0f1e7a29305e35fdd))
* add info into log ([be25d7d](https://github.com/aws-samples/aws-auto-inventory/commit/be25d7de657e556490269bb65c8e60acf95ed738))
* add logging and handle get service data more effectively ([25b7fdd](https://github.com/aws-samples/aws-auto-inventory/commit/25b7fdd8d502784d31e871522b57ad4314420693))
* add more granularity to threading model ([b411dd9](https://github.com/aws-samples/aws-auto-inventory/commit/b411dd922900ea7646c57836bbda8ca0b09c6cfa))
* add threading ([0056396](https://github.com/aws-samples/aws-auto-inventory/commit/0056396d9174ec8432673bf96191780e9e5a7ed7))
* allow developer to set log level ([1301cd9](https://github.com/aws-samples/aws-auto-inventory/commit/1301cd9d939426418678fa756fc94160dacf7565))
* allow user to pass output directory path ([40bd611](https://github.com/aws-samples/aws-auto-inventory/commit/40bd611a6e319609c486ce1833c4e835b6cd867c))
* check aws credentials ([6496c9f](https://github.com/aws-samples/aws-auto-inventory/commit/6496c9f976f9c231d97f0607961b37ab471b5a65))
* cleanup ([7913af6](https://github.com/aws-samples/aws-auto-inventory/commit/7913af681b741d9eca7bec8946b4139d00025716))
* create script to build service sheet ([f418920](https://github.com/aws-samples/aws-auto-inventory/commit/f41892083e636e28ac06df85d527f19b8f3e0cc0))
* improve throttling ([b0c15b0](https://github.com/aws-samples/aws-auto-inventory/commit/b0c15b0721f7ae49e2514bff5fae16883e5aa781))
* include api call with retry ([f17887e](https://github.com/aws-samples/aws-auto-inventory/commit/f17887e11cc501546039d0cf1ef0eb55b9a00a75))
* include output file ([295064e](https://github.com/aws-samples/aws-auto-inventory/commit/295064eb83d9dd7f696fe8328ca8dc2e0b75b9fa))
* make executable ([23aab60](https://github.com/aws-samples/aws-auto-inventory/commit/23aab605794280d8b5423bce197046797b9673a4))
* save log inside output folder, allow user to provide regions ([d46f2df](https://github.com/aws-samples/aws-auto-inventory/commit/d46f2df8b06ee9f7c38f808916bae3949f9e47da))
* save per service ([e1670fd](https://github.com/aws-samples/aws-auto-inventory/commit/e1670fd2554ade17491c02b45cea73f4af41dc35))
* simplify business logic ([1937c75](https://github.com/aws-samples/aws-auto-inventory/commit/1937c75fe97e5f3fce6e29eb66245ceb24d09194))
* use latest python dev container image ([d0e3a70](https://github.com/aws-samples/aws-auto-inventory/commit/d0e3a70f4fb6c947ce5d7a1271de7a845d20c133))


### Bug Fixes

* serialize datetime into string format. ([b60a8dc](https://github.com/aws-samples/aws-auto-inventory/commit/b60a8dc926fad988c331ba1ab962c17c6d49df34))

## [0.7.0](https://github.com/aws-samples/aws-auto-inventory/compare/v0.6.0...v0.7.0) (2023-02-07)


### Features

* only build and hygiene if feat/ or fix/ branches ([042af58](https://github.com/aws-samples/aws-auto-inventory/commit/042af58f709b0cd10b7085674d868bae174ae10a))


### Bug Fixes

* correct glob pattern ([bbbb7e4](https://github.com/aws-samples/aws-auto-inventory/commit/bbbb7e443699a47e4a6b491f1713d028987680c2))
* use main branch, and fix workflow schedule ([acf19d5](https://github.com/aws-samples/aws-auto-inventory/commit/acf19d5b11fc4680c094d0e7d8a8fe2a09d60614))

## [0.6.0](https://github.com/aws-samples/aws-auto-inventory/compare/v0.5.3...v0.6.0) (2023-01-16)


### Features

* use personal access token ([062e5e3](https://github.com/aws-samples/aws-auto-inventory/commit/062e5e3b860ff2bd84861846ed44f917998f83fb))

## [0.5.2](https://github.com/aws-samples/aws-auto-inventory/compare/v0.5.1...v0.5.2) (2023-01-16)


### Bug Fixes

* use v* as tag prefix ([39d1937](https://github.com/aws-samples/aws-auto-inventory/commit/39d19374a350761202999c21b6b15b18672fcb11))

## [0.5.1](https://github.com/aws-samples/aws-auto-inventory/compare/v0.5.0...v0.5.1) (2023-01-16)


### Bug Fixes

* use correct tag format ([18da1b6](https://github.com/aws-samples/aws-auto-inventory/commit/18da1b6e2ad904a465c3e4841a369990d1264d86))

## [0.5.0](https://github.com/aws-samples/aws-auto-inventory/compare/v0.4.0...v0.5.0) (2023-01-16)


### Features

* publish binary once pr has been merged ([45fa76b](https://github.com/aws-samples/aws-auto-inventory/commit/45fa76b8ea7f7dfe758a23e08db4b2abb96043d2))
* publish binary once pr has been merged ([ef6337c](https://github.com/aws-samples/aws-auto-inventory/commit/ef6337c593dec7ef365f330d1733f55b556344e2))


### Bug Fixes

* restore publish workflow ([a16dae5](https://github.com/aws-samples/aws-auto-inventory/commit/a16dae598404b3e176c391b935ffaf5f50b238e7))

## [0.4.0](https://github.com/aws-samples/aws-auto-inventory/compare/v0.3.0...v0.4.0) (2023-01-13)


### Features

* create make target to perform hygiene tasks ([85a4f9d](https://github.com/aws-samples/aws-auto-inventory/commit/85a4f9d852dbee6b9f064b8c640a69692d2acc75))
* ignore output directory and excel files ([9f5a341](https://github.com/aws-samples/aws-auto-inventory/commit/9f5a341ce632a6727ffb07d00d4f7a1fd710d015))

## [0.3.0](https://github.com/aws-samples/aws-auto-inventory/compare/0.2.0...v0.3.0) (2023-01-12)


### Features

* create workflow to release project using gh actions release-please ([905cb08](https://github.com/aws-samples/aws-auto-inventory/commit/905cb08fcd62d1b239302b17357a4325db4876a1))

## Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
