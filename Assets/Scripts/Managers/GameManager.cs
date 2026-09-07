using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// Point central du jeu : chargement de niveaux, Game Over, redémarrage.
/// Singleton persistant entre les scènes.
/// </summary>
public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    [SerializeField] private GameObject gameOverPanel;

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
        DontDestroyOnLoad(gameObject);
    }

    public void LoadLevel(string sceneName)
    {
        Time.timeScale = 1f;
        SceneManager.LoadScene(sceneName);
    }

    public void ReloadCurrentLevel()
    {
        Time.timeScale = 1f;
        SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
    }

    public void ShowGameOver()
    {
        if (gameOverPanel) gameOverPanel.SetActive(true);
        Time.timeScale = 0f;
    }

    public void RestartFromGameOver()
    {
        ReloadCurrentLevel();
    }
}
