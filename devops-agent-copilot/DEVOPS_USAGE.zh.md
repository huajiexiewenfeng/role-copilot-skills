# DevOps 打包与发布使用教程

本文简单说明 `devops-package-copilot` 和 `devops-release-copilot` 的使用方法。

## 1. 打包：devops-package-copilot

用于根据项目里的打包文档和脚本生成镜像、tar 包等构建产物。

适合这样说：

```text
[$devops-package-copilot](C:\Users\admin\.agents\skills\devops-package-copilot\SKILL.md) 打包 server v1.1.2 版本，release
```

常用信息：

- 项目路径：例如 `D:\workspace\drone\zlm\develop\smarthub-mediakit`
- 模块名：例如 `server`、`client`、`server-mysql`
- 版本号：例如 `v1.1.2`
- 类型：例如 `release`

执行时 Copilot 会：

1. 读取项目里的 `docs/docker-build-*.md`。
2. 读取模块配置，例如 `scripts/docker-modules.json`。
3. 按文档调用项目已有脚本，例如 `scripts\docker-build.cmd`。
4. 生成 Docker 镜像和导出的 tar 包。
5. 汇总镜像名、版本、tar 包路径和失败原因。

示例结果：

```text
smarthub-mediakit-server-release:v1.1.2
smarthub-mediakit-server-mysql-release:v1.1.2
server-images-v1.1.2-20260603-135806.tar
```

## 2. 发布准备：devops-release-copilot

用于把打包后的镜像版本同步到部署目录里的 Docker Compose 文件。

适合这样说：

```text
[$devops-release-copilot](C:\Users\admin\.codex\skills\devops-release-copilot\SKILL.md) 更新到 D:\workspace\drone\smarthub-deploy\deploy\v1.3.1\服务器+工控机\cloud
```

常用信息：

- 部署目录：例如 `D:\workspace\drone\smarthub-deploy\deploy\v1.3.1\服务器+工控机\cloud`
- 镜像版本：例如 `v1.1.2`
- 需要更新的服务：例如 `mediakit-server`、`mediakit-server-mysql`

执行时 Copilot 会：

1. 找到部署目录下的 `*.yml` 和 `*.yaml`。
2. 定位对应服务的 `image:` 行。
3. 更新 release 镜像 tag。
4. 对 Java/Spring 服务检查 `application*.yml` 或 `application*.properties` 中的环境变量。
5. 把缺失的环境变量补到 compose 的 `environment` 中。
6. 保留已有 compose 变量，不覆盖用户已经配置的值。
7. 输出本次更新的文件、镜像 tag 和新增环境变量。

示例更新：

```yaml
mediakit-server:
  image: smarthub-mediakit-server-release:v1.1.2
```

```yaml
mediakit-server-mysql:
  image: smarthub-mediakit-server-mysql-release:v1.1.2
```

## 3. 打包加发布的一句话用法

```text
[$devops-package-copilot](C:\Users\admin\.agents\skills\devops-package-copilot\SKILL.md) 打包 server v1.1.2 版本，release，然后再 [$devops-release-copilot](C:\Users\admin\.codex\skills\devops-release-copilot\SKILL.md) 更新到 D:\workspace\drone\smarthub-deploy\deploy\v1.3.1\服务器+工控机\cloud
```

Copilot 会先打包，成功后再更新部署文件。

## 4. 注意事项

- 打包规则以项目自己的 `docs/docker-build-*.md` 为准。
- 发布更新只改指定部署目录，不会自动部署或重启服务。
- `devops-release-copilot` 更新 Java/Spring 服务时，默认需要同步新增环境变量。
- 如果只想改镜像 tag，要明确说明“只更新 image tag”。
- 如果目录里已有其他未提交改动，Copilot 只处理本次请求相关文件。