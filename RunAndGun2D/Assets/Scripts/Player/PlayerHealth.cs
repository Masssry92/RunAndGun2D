using UnityEngine;

/// <summary>
/// Relie le composant générique Health au joueur : désactive les contrôles
/// et déclenche l'écran de Game Over lorsque le joueur meurt.
/// </summary>
[RequireComponent(typeof(Health))]
public class PlayerHealth : MonoBehaviour
{
    private Health health;

    private void Awake()
    {
        health = GetComponent<Health>();
        health.OnDeath.AddListener(HandleDeath);
    }

    private void HandleDeath()
    {
        if (TryGetComponent(out PlayerController controller)) controller.enabled = false;
        if (TryGetComponent(out PlayerShooting shooting)) shooting.enabled = false;

        if (GameManager.Instance != null)
        {
            GameManager.Instance.ShowGameOver();
        }
    }
}
