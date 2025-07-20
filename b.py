def plot_robot_3d(thetas):
    fig = plt.figure(figsize=(14, 12))
    ax = fig.add_subplot(111, projection='3d')
    
    # Calcular todas las transformaciones
    T = np.eye(4)
    points = [T[:3, 3]]  # Comienza en el origen
    transforms = []
    
    for i in range(6):
        T = T @ dh_matrix(thetas[i], dh_params[i]['d'], dh_params[i]['a'], dh_params[i]['alpha'])
        transforms.append(T)
        points.append(T[:3, 3])
    
    points = np.array(points)
    
    # Configuración estética
    plt.style.use('seaborn-darkgrid')
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')
    
    # Dibujar el esqueleto del robot
    ax.plot(points[:,0], points[:,1], points[:,2], 
            'o-', linewidth=3, markersize=10, 
            color='#4682B4', markerfacecolor='#FF7F50', 
            markeredgewidth=2, markeredgecolor='black', 
            label='Cadena cinemática')
    
    # Dibujar marcos de referencia
    def draw_frame(T, length=75, alpha=0.7, label=None):
        colors = ['#FF0000', '#00AA00', '#0000FF']  # R, G, B más suaves
        labels = ['X', 'Y', 'Z'] if label else [None, None, None]
        for i, (c, l) in enumerate(zip(colors, labels)):
            ax.quiver(T[0,3], T[1,3], T[2,3], 
                     T[0,i], T[1,i], T[2,i], 
                     color=c, length=length, 
                     linewidth=2, arrow_length_ratio=0.15,
                     alpha=alpha, label=l if label and i==0 else None)
    
    # Dibujar marcos importantes
    draw_frame(transforms[0], length=100, label='Base')  # Marco base
    draw_frame(transforms[-1], length=75, label='Efector')  # Marco efector final
    draw_frame(T_deseada, length=100, alpha=1, label='Deseado')  # Marco deseado
    
    # Puntos clave con mejor visualización
    ax.scatter(points[-1,0], points[-1,1], points[-1,2], 
               color='red', s=300, marker='*', 
               edgecolor='black', linewidth=1, 
               label='Posición calculada')
    
    ax.scatter(T_deseada[0,3], T_deseada[1,3], T_deseada[2,3], 
               color='green', s=300, marker='D', 
               edgecolor='black', linewidth=1, 
               label='Posición deseada')
    
    # Configuración de ejes y leyenda
    ax.set_xlabel('X (mm)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Y (mm)', fontsize=12, fontweight='bold')
    ax.set_zlabel('Z (mm)', fontsize=12, fontweight='bold')
    
    title = f'Cinemática inversa UR5e\nPosición: {posicion_deseada} mm\nOrientación: RPY({np.round(np.degrees(roll_deseado))}°, {np.round(np.degrees(pitch_deseado))}°, {np.round(np.degrees(yaw_deseado))}°)'
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Ajustar límites dinámicamente
    all_points = np.vstack([points, T_deseada[:3,3]])
    max_range = np.ptp(all_points) * 1.2
    mid_x, mid_y, mid_z = np.mean(all_points, axis=0)
    
    ax.set_xlim(mid_x - max_range/2, mid_x + max_range/2)
    ax.set_ylim(mid_y - max_range/2, mid_y + max_range/2)
    ax.set_zlim(0, max_range)  # El robot siempre parte de z=0
    
    # Mejorar la leyenda
    leg = ax.legend(fontsize=10, loc='upper right', 
                   bbox_to_anchor=(1.15, 1), 
                   title="Elementos:", title_fontsize=11)
    leg.get_frame().set_alpha(1)
    leg.get_frame().set_facecolor('white')
    
    # Cuadrícula y vista
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('lightgray')
    ax.yaxis.pane.set_edgecolor('lightgray')
    ax.zaxis.pane.set_edgecolor('lightgray')
    
    # Vista inicial más informativa
    ax.view_init(elev=30, azim=45)
    
    # Añadir texto informativo
    error_pos = np.linalg.norm(T_calculada[:3,3] - T_deseada[:3,3])
    error_rot = np.arccos((np.trace(T_calculada[:3,:3].T @ T_deseada[:3,:3]) - 1)/2)
    
    info_text = f'Error posición: {error_pos:.2f} mm\nError orientación: {np.degrees(error_rot):.2f}°'
    ax.text2D(0.02, 0.98, info_text, transform=ax.transAxes,
             fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.show()