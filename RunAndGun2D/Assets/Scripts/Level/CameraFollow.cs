using UnityEngine;

/// <summary>Fait suivre la caméra au joueur, avec un léger lissage et des limites optionnelles.</summary>
public class CameraFollow : MonoBehaviour
{
    [SerializeField] private Transform target;
    [SerializeField] private float smoothTime = 0.15f;
    [SerializeField] private Vector2 offset = new Vector2(0f, 1f);

    [Header("Limites (optionnel)")]
    [SerializeField] private bool useBounds = false;
    [SerializeField] private Vector2 minBounds;
    [SerializeField] private Vector2 maxBounds;

    private Vector3 velocity;

    private void LateUpdate()
    {
        if (!target) return;

        Vector3 desired = new Vector3(target.position.x + offset.x, target.position.y + offset.y, transform.position.z);
        Vector3 smoothed = Vector3.SmoothDamp(transform.position, desired, ref velocity, smoothTime);

        if (useBounds)
        {
            smoothed.x = Mathf.Clamp(smoothed.x, minBounds.x, maxBounds.x);
            smoothed.y = Mathf.Clamp(smoothed.y, minBounds.y, maxBounds.y);
        }

        transform.position = smoothed;
    }

    public void SetTarget(Transform t) => target = t;
}
