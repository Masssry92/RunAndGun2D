using UnityEngine;
using UnityEngine.Events;

/// <summary>
/// Composant générique de points de vie, réutilisable par le joueur ET les ennemis
/// (principe d'encapsulation / composition plutôt que duplication de code).
/// </summary>
[DisallowMultipleComponent]
public class Health : MonoBehaviour
{
    [Header("Points de vie")]
    [SerializeField] private int maxHealth = 3;
    [SerializeField] private float invulnerabilityDuration = 0.5f;

    [Header("Événements")]
    public UnityEvent<int, int> OnHealthChanged; // (vie actuelle, vie max)
    public UnityEvent OnDamaged;
    public UnityEvent OnDeath;

    public int MaxHealth => maxHealth;
    public int CurrentHealth { get; private set; }
    public bool IsDead { get; private set; }

    private float invulnerableUntil = -1f;

    private void Awake()
    {
        CurrentHealth = maxHealth;
    }

    /// <summary>Inflige des dégâts, en tenant compte d'une courte invulnérabilité après un coup.</summary>
    public void TakeDamage(int amount)
    {
        if (IsDead || amount <= 0) return;
        if (Time.time < invulnerableUntil) return;

        CurrentHealth = Mathf.Max(0, CurrentHealth - amount);
        invulnerableUntil = Time.time + invulnerabilityDuration;

        OnHealthChanged?.Invoke(CurrentHealth, maxHealth);
        OnDamaged?.Invoke();

        if (CurrentHealth <= 0 && !IsDead)
        {
            IsDead = true;
            OnDeath?.Invoke();
        }
    }

    public void Heal(int amount)
    {
        if (IsDead || amount <= 0) return;
        CurrentHealth = Mathf.Min(maxHealth, CurrentHealth + amount);
        OnHealthChanged?.Invoke(CurrentHealth, maxHealth);
    }

    public void ResetHealth()
    {
        CurrentHealth = maxHealth;
        IsDead = false;
        OnHealthChanged?.Invoke(CurrentHealth, maxHealth);
    }
}
