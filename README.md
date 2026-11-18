# 3D Animation Short Generator — versi Google Antigravity

Port dari skill MiniMax Hub [`3d-animation-short-generator`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/3d-animation-short-generator/SKILL.md) (v0.5.4) supaya jalan di **Google Antigravity**. Alur kerjanya sama persis (brief → cerita → kartu karakter/scene → tabel shot 6 kolom → storyboard → klip → rakit + BGM). Yang diganti hanya lapisan platform.

## Apa yang diganti

| Asli (MiniMax Hub) | Versi Antigravity |
|---|---|
| Canvas | Folder `animation/<slug>/` di workspace (file bernomor 00–10) |
| Choice card | Daftar pilihan bernomor di chat; agent **berhenti dan menunggu** jawabanmu |
| Generate gambar di Hub | Generator gambar bawaan Antigravity (Nano Banana Pro). Cadangan: `scripts/gen_image.py` |
| Video H3 / Seedance 2.0 | **Veo 3.1** (final) / **Veo 3.1 Fast** (draft) lewat `scripts/veo_generate.py` |
| Klip H3 sampai 15 dtk | Klip Veo **4 / 6 / 8 dtk**. Tabel shot otomatis memecah adegan yang lebih panjang |
| Rakit + BGM di Hub | `scripts/assemble.sh` (ffmpeg: urutkan klip, crop 1:1/4:5, BGM otomatis mengecil saat ada dialog) |

Mode render baru, **keyframe** (default): Nano Banana Pro membuat frame pertama tiap shot dari kartu karakter + scene, lalu Veo menganimasikannya. Cara ini jauh lebih konsisten daripada text-to-video murni.

## Model di Antigravity

| Tahap | Model agent yang disarankan (dropdown Antigravity) |
|---|---|
| Brief, cerita, tabel shot, storyboard | Gemini Pro tier (High thinking) atau Claude Opus/Sonnet |
| Kartu karakter/scene | Gemini Pro tier (pakai Nano Banana Pro bawaan) |
| Script, ffmpeg, urus file | Gemini Flash tier |

Untuk generasi video dan gambar lewat script (via Gemini API):
- `VEO_MODEL` default `veo-3.1-generate-preview` (atau `veo-3.1-fast-generate-preview`)
- `IMAGE_MODEL` default `gemini-3-pro-image-preview`

ID model preview sering diganti Google. Kalau muncul error "model not found", cek daftar model yang tersedia (perintahnya ada di `references/model-selection.md`), lalu ganti lewat env var tanpa perlu mengedit script.

## Instalasi

**Per project** (skill hanya aktif di workspace itu):
```bash
mkdir -p /path/ke/project/.agents/skills
cp -R .agents/skills/3d-animation-short-generator /path/ke/project/.agents/skills/
```

**Global** (aktif di semua workspace). Lokasi folder global berbeda antar versi Antigravity. Cek dokumentasi Antigravity yang terpasang, biasanya salah satu dari ini:
```bash
cp -R .agents/skills/3d-animation-short-generator ~/.gemini/antigravity/skills/
# atau ~/.gemini/config/skills/
```
Antigravity versi lama memakai `.agent/skills/` (tanpa "s"). Kalau skill tidak terdeteksi, coba path itu.

**Untuk tahap video (Step 7–8):**
```bash
pip install google-genai
brew install ffmpeg          # sudah terpasang di Mac ini
export GEMINI_API_KEY=...    # dari Google AI Studio, billing harus aktif (Veo berbayar)
```
Taruh API key di shell (`~/.zshrc`), jangan di-paste ke chat agent.

## Cara pakai

Di Antigravity (mode **Planning**), ketik misalnya:
> Buatkan film animasi 3D pendek: kucing oranye yang takut hujan tapi harus menyelamatkan anak burung.

Agent akan menanyakan rasio layar dan durasi, lalu berjalan per tahap dan berhenti di setiap gerbang persetujuan. Sebelum render massal, S01 dirender dulu sebagai tes supaya biaya terkontrol.

## Isi folder

```
.agents/skills/3d-animation-short-generator/
  SKILL.md                      # instruksi utama (versi Antigravity)
  references/
    model-selection.md          # ditulis ulang: Veo 3.1, Nano Banana Pro, mode keyframe/reference, biaya
    fallback-policy.md          # ditulis ulang: tangga retry Veo, error API/kuota/safety
    shot-table-spec.md          # dari aslinya + patch (durasi 4/6/8 dtk, istilah Veo)
    storyboard-guidelines.md    # dari aslinya + catatan port
    qc-checklist.md             # dari aslinya + catatan port
  scripts/
    veo_generate.py             # render 1 klip (keyframe / reference / last-frame)
    gen_image.py                # kartu & keyframe dengan gambar referensi
    assemble.sh                 # rakit film + BGM ducking (sudah diuji dengan klip dummy)
upstream/                       # salinan asli dari repo MiniMax, untuk perbandingan
```

## Catatan

- Repo MiniMax-H3 tidak mencantumkan file LICENSE. Port ini aman untuk dipakai sendiri. Kalau mau dipublikasikan ulang, cek dulu izinnya ke pemilik repo.
- Veo memproduksi audio per klip, jadi BGM yang menyambung sepanjang film harus berasal dari file musik terpisah (milikmu sendiri atau dari library bebas royalti). Agent akan menanyakan ini di Step 8.
- Rasio 1:1 dan 4:5 dirender dalam 16:9 / 9:16, lalu di-crop di tengah saat perakitan. Karena itu, minta agent menjaga aksi tetap di area tengah frame.
