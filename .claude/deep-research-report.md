1. **Vite 7.x (vite@7.2.4) Node requirement:** Node.js >= 20.19.0 (and for Node 22, >= 22.12.0)【1†L168-L170】.  
2. **NodeSource install command on Ubuntu 20.04 (2025/26):**  
   - For Node 22 LTS:  
     ``curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash -``【16†L12-L16】  
   - For Node 20 LTS:  
     ``curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -``【26†L1-L4】.  
3. **pywebview 3.x vs Python 3.12:**  Pywebview v3.7/3.x predates Python 3.12 and is broken by removal of `distutils`【55†L140-L145】. The first version supporting Python 3.12 is in the 5.x series (e.g. pywebview v5.3.2, Oct 2025)【57†L570-L577】.  
4. **Lubuntu 20.04 (LXQt) GTK/WebKit packages:** Same as Ubuntu GNOME. You need `python3-gi`, `python3-gi-cairo`, `gir1.2-gtk-3.0` and `gir1.2-webkit2-4.0` (or 4.1)【61†L111-L115】. No additional LXQt-specific packages are required.  
5. **uv installer compatibility:** Yes. The Astral `uv` installer targets glibc >= 2.17【68†L188-L196】, and Ubuntu 20.04 has glibc 2.31. So `curl -LsSf https://astral.sh/uv/install.sh | sh` works on Ubuntu 20.04. (As an alternative, you can use the Snap: `sudo snap install astral-uv --classic`【69†L162-L169】.)  

**Sources:** Official Vite and pywebview docs, NodeSource setup scripts【1†L168-L170】【16†L12-L16】【26†L1-L4】【55†L140-L145】【57†L570-L577】【61†L111-L115】【68†L188-L196】.