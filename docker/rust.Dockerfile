# MK64 native rebuild toolchain: pinned Rust 1.89.0 with rustfmt and clippy, non-root, no secrets.
FROM rust:1.89.0-slim-bookworm@sha256:294917190b5a3fed18d3303213943f40ec9b644b3cd6e5cdc8cd029334a770b3

ENV CARGO_HOME=/usr/local/cargo \
    RUSTUP_HOME=/usr/local/rustup \
    RUSTUP_TOOLCHAIN=1.89.0-x86_64-unknown-linux-gnu \
    CARGO_TARGET_DIR=/work/target \
    PATH=/usr/local/cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && rustup component add --toolchain 1.89.0-x86_64-unknown-linux-gnu rustfmt clippy \
    && groupadd --gid 1000 mk64 \
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash mk64 \
    && mkdir -p /work \
    && chown 1000:1000 /work \
    && rm -f /usr/local/cargo/.package-cache

USER 1000:1000

WORKDIR /work

CMD ["/bin/bash"]
