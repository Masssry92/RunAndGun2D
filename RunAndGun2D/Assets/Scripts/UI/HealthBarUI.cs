using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Met à jour une barre de vie (Image en mode "Filled") à partir d'un composant Health.
/// À placer sur une UI Image dans un Canvas, avec le champ Target Health assigné au joueur.
/// </summary>
public class HealthBarUI : MonoBehaviour
{
    [SerializeField] private Health targetHealth;
    [SerializeField] private Image fillImage;

    private void Start()
    {
        if (targetHealth)
        {
            targetHealth.OnHealthChanged.AddListener(UpdateBar);
            UpdateBar(targetHealth.CurrentHealth, targetHealth.MaxHealth);
        }
    }

    private void UpdateBar(int current, int max)
    {
        if (fillImage) fillImage.fillAmount = max > 0 ? (float)current / max : 0f;
    }
}
