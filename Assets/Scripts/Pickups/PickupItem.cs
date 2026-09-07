using UnityEngine;

public enum PickupType
{
    Health,
    Ammo
}

/// <summary>Bonus ramassable (vie ou munitions) détecté via un Collider2D en Trigger.</summary>
[RequireComponent(typeof(Collider2D))]
public class PickupItem : MonoBehaviour
{
    [SerializeField] private PickupType type = PickupType.Health;
    [SerializeField] private int amount = 1;
    [SerializeField] private string targetTag = "Player";

    private void Reset()
    {
        GetComponent<Collider2D>().isTrigger = true;
    }

    private void OnTriggerEnter2D(Collider2D other)
    {
        if (!other.CompareTag(targetTag)) return;

        if (type == PickupType.Health && other.TryGetComponent(out Health health))
        {
            health.Heal(amount);
            Destroy(gameObject);
        }
        else if (type == PickupType.Ammo && other.TryGetComponent(out PlayerShooting shooting))
        {
            shooting.RefillAmmo(amount);
            Destroy(gameObject);
        }
    }
}
