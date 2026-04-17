import tkinter as tk
from tkinter import ttk, messagebox
import copy

# ============================================================
#  LOGIQUE DE RÉSOLUTION (A*)
# ============================================================
ETAT_FINAL = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

def h(t):
    mal_places = 0
    for y in range(3):
        for x in range(3):
            val = t[y][x]
            if val != 0 and val != ETAT_FINAL[y][x]:
                mal_places += 1
    return mal_places

def position_case_vide(t):
    for y in range(3):
        for x in range(3):
            if t[y][x] == 0: return (x, y)

def transitions(t):
    x, y = position_case_vide(t)
    voisins = []
    for nx, ny in [(x, y-1), (x, y+1), (x-1, y), (x+1, y)]:
        if 0 <= nx < 3 and 0 <= ny < 3:
            nouveau = copy.deepcopy(t)
            nouveau[y][x], nouveau[ny][nx] = nouveau[ny][nx], nouveau[y][x]
            voisins.append(nouveau)
    return voisins

def astar(etat_initial):
    # Transformation en tuple pour le set 'visited'
    def to_tp(t): return tuple(tuple(l) for l in t)
    
    start_tp = to_tp(etat_initial)
    # format: (f, g, etat, chemin)
    queue = [(h(etat_initial), 0, etat_initial, [etat_initial])]
    visited = {start_tp: 0}

    while queue:
        # Tri par f (le plus petit en premier)
        queue.sort(key=lambda x: x[0])
        f, g, etat, chemin = queue.pop(0)

        if etat == ETAT_FINAL:
            return chemin

        for v in transitions(etat):
            v_tp = to_tp(v)
            nouv_g = g + 1
            if v_tp not in visited or nouv_g < visited[v_tp]:
                visited[v_tp] = nouv_g
                queue.append((nouv_g + h(v), nouv_g, v, chemin + [v]))
    return None

# ============================================================
#  INTERFACE GRAPHIQUE INTERACTIVE
# ============================================================

class TaquinInteractif:
    def __init__(self, root):
        self.root = root
        self.root.title("Taquin A* Interactif")
        self.root.geometry("420x600")
        self.root.configure(bg="#2c3e50")

        # État initial par défaut
        self.etat = [[1, 2, 3], [4, 5, 6], [0, 7, 8]]
        self.en_animation = False
        self.vitesse = 0.5

        self.setup_ui()
        self.dessiner_plateau()

    def setup_ui(self):
        # Titre et Instructions
        tk.Label(self.root, text="Notre taquin", font=("Helvetica", 18, "bold"), 
                 bg="#2c3e50", fg="#ecf0f1", pady=10).pack()
        
        self.info_label = tk.Label(self.root, text="Cliquez sur une case pour la déplacer", 
                                   bg="#2c3e50", fg="#bdc3c7", font=("Helvetica", 10))
        self.info_label.pack()

        # Zone du plateau
        self.frame_plateau = tk.Frame(self.root, bg="#34495e", bd=8, relief="flat")
        self.frame_plateau.pack(pady=15)

        # Boutons de contrôle
        btn_frame = tk.Frame(self.root, bg="#2c3e50")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Résoudre (IA)", command=self.lancer_ia,
                  bg="#27ae60", fg="white", width=15, font=("Helvetica", 10, "bold")).grid(row=0, column=0, padx=5)
        
        
        # Slider de vitesse
        tk.Label(self.root, text="Vitesse de l'IA", bg="#2c3e50", fg="#bdc3c7").pack()
        self.slider = ttk.Scale(self.root, from_=0.1, to_=1.0, orient="horizontal", command=self.set_vitesse)
        self.slider.set(0.6)
        self.slider.pack(fill="x", padx=60)

    def set_vitesse(self, val):
        self.vitesse = float(val)

    def dessiner_plateau(self):
        # On vide la frame et on recrée les boutons pour chaque case
        for widget in self.frame_plateau.winfo_children():
            widget.destroy()

        for y in range(3):
            for x in range(3):
                val = self.etat[y][x]
                txt = str(val) if val != 0 else ""
                bg_color = "#3498db" if val != 0 else "#34495e"
                
                # Création d'un bouton pour chaque chiffre
                # On passe les coordonnées x, y à la fonction de clic
                btn = tk.Button(self.frame_plateau, text=txt, font=("Helvetica", 20, "bold"),
                                width=5, height=2, bg=bg_color, fg="white", relief="flat",
                                command=lambda px=x, py=y: self.cliquer_case(px, py))
                btn.grid(row=y, column=x, padx=3, pady=3)

    def cliquer_case(self, x, y):
        """ Gère le déplacement manuel si on clique sur une case adjacente au vide """
        if self.en_animation: return # Désactiver pendant que l'IA joue

        vx, vy = position_case_vide(self.etat)
        
        # Vérifier si la case cliquée est à côté de la case vide (Manhattan distance == 1)
        if abs(x - vx) + abs(y - vy) == 1:
            self.etat[vy][vx], self.etat[y][x] = self.etat[y][x], self.etat[vy][vx]
            self.dessiner_plateau()
            
            if self.etat == ETAT_FINAL:
                messagebox.showinfo("Bravo", "Vous avez résolu le taquin !")

    def lancer_ia(self):
        if self.en_animation: return
        self.en_animation = True
        self.info_label.config(text="L'IA réfléchit...", fg="#f1c40f")
        self.root.update()

        chemin = astar(self.etat)
        
        if chemin:
            self.animer_ia(chemin[1:])
        else:
            messagebox.showerror("Erreur", "Impossible de résoudre cette configuration.")
            self.en_animation = False

    def animer_ia(self, etapes):
        if not etapes:
            self.en_animation = False
            self.info_label.config(text="Résolution terminée !", fg="#2ecc71")
            return

        self.etat = etapes.pop(0)
        self.dessiner_plateau()
        
        # Calcul du délai (inversement proportionnel à la vitesse)
        delai = int((1.1 - self.vitesse) * 800)
        self.root.after(delai, lambda: self.animer_ia(etapes))

    def reset(self):
        self.en_animation = False
        self.etat = [[1, 2, 3], [4, 5, 6], [0, 7, 8]]
        self.info_label.config(text="Mode manuel activé", fg="#bdc3c7")
        self.dessiner_plateau()

if __name__ == "__main__":
    root = tk.Tk()
    app = TaquinInteractif(root)
    root.mainloop()
