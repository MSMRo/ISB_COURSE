import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

def analizar_sistema(b, a, nombre="Sistema"):
    """
    Grafica el Plano Z (Polos y Ceros), Magnitud (dB) y Fase (grados)
    de un sistema discreto definido por H(z) = B(z)/A(z).
    """
    # 1. Obtener ceros, polos y ganancia
    zeros, poles, _ = signal.tf2zpk(b, a)
    
    # 2. Calcular respuesta en frecuencia (evaluando sobre el círculo unitario)
    w, h = signal.freqz(b, a, worN=1024)
    freq_norm = w / np.pi  # Frecuencia normalizada (0 a 1 corresponde a 0 a pi rad/muestra)
    
    # Magnitud en dB (evitando log10(0) con un epsilon muy pequeño)
    magnitud_db = 20 * np.log10(np.maximum(np.abs(h), 1e-10))
    
    # Fase desenvuelta en grados
    fase_deg = np.rad2deg(np.unwrap(np.angle(h)))
    
    # --- CONFIGURACIÓN DE GRÁFICAS ---
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    fig.suptitle(f"Análisis Completo: {nombre}", fontsize=14, fontweight='bold')
    
    # PANEL 1: Diagrama de Polos y Ceros
    ax_z = axes[0]
    circulo = plt.Circle((0, 0), 1, color='gray', fill=False, linestyle='--', linewidth=1.2)
    ax_z.add_patch(circulo)
    ax_z.scatter(np.real(zeros), np.imag(zeros), s=90, facecolors='none', edgecolors='tab:blue', linewidths=2, label='Ceros (o)')
    ax_z.scatter(np.real(poles), np.imag(poles), s=90, marker='x', color='tab:red', linewidths=2, label='Polos (x)')
    
    ax_z.axhline(0, color='black', linewidth=0.6)
    ax_z.axvline(0, color='black', linewidth=0.6)
    ax_z.set_xlim([-1.4, 1.4])
    ax_z.set_ylim([-1.4, 1.4])
    ax_z.set_aspect('equal')
    ax_z.set_title("Plano Z (Polos y Ceros)")
    ax_z.set_xlabel("Parte Real")
    ax_z.set_ylabel("Parte Imaginaria")
    ax_z.grid(True, alpha=0.3)
    ax_z.legend(loc="upper right")
    
    # PANEL 2: Respuesta en Magnitud
    ax_mag = axes[1]
    ax_mag.plot(freq_norm, magnitud_db, color='tab:green', linewidth=2)
    ax_mag.set_title("Respuesta en Magnitud")
    ax_mag.set_xlabel("Frecuencia Normalizada (×π rad/muestra)")
    ax_mag.set_ylabel("Magnitud (dB)")
    ax_mag.grid(True, alpha=0.3)
    
    # PANEL 3: Respuesta en Fase
    ax_fase = axes[2]
    ax_fase.plot(freq_norm, fase_deg, color='tab:purple', linewidth=2)
    ax_fase.set_title("Respuesta en Fase")
    ax_fase.set_xlabel("Frecuencia Normalizada (×π rad/muestra)")
    ax_fase.set_ylabel("Fase (grados)")
    ax_fase.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def analizar_sistema_s(num, den, nombre="Sistema Continuo", w_range=(0.1, 1000)):
    """
    Grafica el Plano S (Polos y Ceros), Diagrama de Bode (Magnitud y Fase)
    y la Respuesta al Escalón en tiempo continuo.
    """
    sys = signal.TransferFunction(num, den)
    zeros, poles, _ = signal.tf2zpk(num, den)
    
    # Calcular Bode (en rad/s)
    w = np.logspace(np.log10(w_range[0]), np.log10(w_range[1]), 1000)
    w, mag, phase = signal.bode(sys, w=w)
    
    # Calcular Respuesta al Escalón en el tiempo
    t, y = signal.step(sys)
    
    # --- CONFIGURACIÓN DE GRÁFICAS ---
    fig, axes = plt.subplots(1, 4, figsize=(18, 4.2))
    fig.suptitle(f"Análisis Dominio S: {nombre}", fontsize=13, fontweight='bold')
    
    # PANEL 1: Plano S (Polos y Ceros)
    ax_s = axes[0]
    ax_s.axvline(0, color='gray', linestyle='--', linewidth=1.2, label='Eje jω (Límite estabilidad)')
    ax_s.axhline(0, color='black', linewidth=0.6)
    
    ax_s.scatter(np.real(zeros), np.imag(zeros), s=90, facecolors='none', edgecolors='tab:blue', linewidths=2, label='Ceros (o)')
    ax_s.scatter(np.real(poles), np.imag(poles), s=90, marker='x', color='tab:red', linewidths=2, label='Polos (x)')
    
    # Ajustar límites del plano S dinámicamente
    all_re = np.concatenate([np.real(poles), np.real(zeros), [-1]])
    all_im = np.concatenate([np.imag(poles), np.imag(zeros), [1]])
    max_re = max(abs(np.min(all_re)), abs(np.max(all_re))) * 1.3
    max_im = max(abs(np.min(all_im)), abs(np.max(all_im))) * 1.3
    
    ax_s.set_xlim([-max_re, max_re * 0.3])  # Mostramos más el semiplano izquierdo
    ax_s.set_ylim([-max_im, max_im])
    ax_s.set_title("Plano S (Polos y Ceros)")
    ax_s.set_xlabel("Parte Real (σ)")
    ax_s.set_ylabel("Parte Imaginaria (jω)")
    ax_s.grid(True, alpha=0.3)
    ax_s.legend(loc="upper right", fontsize=8)
    
    # PANEL 2: Bode - Magnitud (escala logarítmica)
    ax_mag = axes[1]
    ax_mag.semilogx(w, mag, color='tab:green', linewidth=2)
    ax_mag.set_title("Bode: Magnitud")
    ax_mag.set_xlabel("Frecuencia ω (rad/s)")
    ax_mag.set_ylabel("Magnitud (dB)")
    ax_mag.grid(True, which="both", alpha=0.3)
    
    # PANEL 3: Bode - Fase
    ax_fase = axes[2]
    ax_fase.semilogx(w, phase, color='tab:purple', linewidth=2)
    ax_fase.set_title("Bode: Fase")
    ax_fase.set_xlabel("Frecuencia ω (rad/s)")
    ax_fase.set_ylabel("Fase (grados)")
    ax_fase.grid(True, which="both", alpha=0.3)
    
    # PANEL 4: Respuesta al Escalón en el tiempo
    ax_step = axes[3]
    ax_step.plot(t, y, color='tab:orange', linewidth=2)
    ax_step.axhline(1.0, color='gray', linestyle=':', linewidth=1)
    ax_step.set_title("Respuesta al Escalón y(t)")
    ax_step.set_xlabel("Tiempo (s)")
    ax_step.set_ylabel("Amplitud")
    ax_step.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()