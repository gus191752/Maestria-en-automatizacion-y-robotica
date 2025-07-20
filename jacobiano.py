import numpy as np

def jacobian_transpose_ik(T_deseada, theta_inicial, max_iter=1000, alpha=0.01, tol=1e-6):
    theta = theta_inicial.copy()
    for _ in range(max_iter):
        T_actual = forward_kinematics(theta)  # Cinemática directa
        error_pos = T_deseada[:3, 3] - T_actual[:3, 3]
        error_ori = orientation_error(T_deseada[:3, :3], T_actual[:3, :3])
        error = np.concatenate([error_pos, error_ori])
        
        if np.linalg.norm(error) < tol:
            break
            
        J = compute_jacobian(theta)  # Calcular Jacobiano
        theta += alpha * J.T @ error  # Actualizar theta
        
    return theta


