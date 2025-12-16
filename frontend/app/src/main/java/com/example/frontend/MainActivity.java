package com.example.frontend;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.cardview.widget.CardView;

import com.bumptech.glide.Glide;
import com.bumptech.glide.load.engine.GlideException;
import com.bumptech.glide.request.RequestListener;
import com.bumptech.glide.request.target.Target;

public class MainActivity extends AppCompatActivity {
    private static final String TAG = "MainActivity";
    private Button ringButton;
    private Button unlockButton;
    private Button historyButton;
    private ImageView photoImageView;
    private ProgressBar loadingProgress;
    private TextView statusText;
    private CardView photoCard;

    private ApiService apiService;
    private Visit currentVisit;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        ringButton = findViewById(R.id.ringButton);
        unlockButton = findViewById(R.id.unlockButton);
        historyButton = findViewById(R.id.historyButton);
        photoImageView = findViewById(R.id.photoImageView);
        loadingProgress = findViewById(R.id.loadingProgress);
        statusText = findViewById(R.id.statusText);
        photoCard = findViewById(R.id.photoCard);

        apiService = new ApiService();

        ringButton.setOnClickListener(v -> handleRingDoorbell());
        unlockButton.setOnClickListener(v -> handleUnlockDoor());
    }

    private void handleRingDoorbell() {
        setLoadingState(true);
        statusText.setText("Звоним в дверь...");
        hideVisitorInfo();

        apiService.ringDoorbell(new ApiService.ApiCallback<Visit>() {
            @Override
            public void onSuccess(Visit visit) {
                currentVisit = visit;
                setLoadingState(false);
                statusText.setText("Кто-то пришел!");
                showVisitorInfo(visit);
            }

            @Override
            public void onError(String error) {
                setLoadingState(false);
                statusText.setText("Ошибка: " + error);
                Toast.makeText(MainActivity.this, error, Toast.LENGTH_LONG).show();
            }
        });
    }

    private void handleUnlockDoor() {
        unlockButton.setEnabled(false);
        statusText.setText("Открываем дверь...");

        apiService.unlockDoor(new ApiService.ApiCallback<String>() {
            @Override
            public void onSuccess(String message) {
                statusText.setText(message);
                Toast.makeText(MainActivity.this, message, Toast.LENGTH_SHORT).show();

                photoImageView.postDelayed(() -> {
                    hideVisitorInfo();
                    statusText.setText("Готов к новому звонку");
                    unlockButton.setEnabled(true);
                }, 2000);
            }

            @Override
            public void onError(String error) {
                statusText.setText("Ошибка: " + error);
                Toast.makeText(MainActivity.this, error, Toast.LENGTH_LONG).show();
                unlockButton.setEnabled(true);
            }
        });
    }

    private void showVisitorInfo(Visit visit) {
        photoCard.setVisibility(View.VISIBLE);
        unlockButton.setVisibility(View.VISIBLE);

        String photoUrl = visit.getPhotoUrl();
        Log.d(TAG, "Loading photo from URL: " + photoUrl);

        Glide.with(this)
                .load(photoUrl)
                .placeholder(android.R.drawable.ic_menu_camera)
                .error(android.R.drawable.ic_menu_report_image)
                .listener(new RequestListener<android.graphics.drawable.Drawable>() {
                    @Override
                    public boolean onLoadFailed(GlideException e, Object model, Target<android.graphics.drawable.Drawable> target, boolean isFirstResource) {
                        Log.e(TAG, "Failed to load image from: " + photoUrl, e);
                        Toast.makeText(MainActivity.this, "Ошибка загрузки фото", Toast.LENGTH_LONG).show();
                        return false;
                    }

                    @Override
                    public boolean onResourceReady(android.graphics.drawable.Drawable resource, Object model, Target<android.graphics.drawable.Drawable> target, com.bumptech.glide.load.DataSource dataSource, boolean isFirstResource) {
                        Log.d(TAG, "Image loaded successfully from: " + photoUrl);
                        return false;
                    }
                })
                .into(photoImageView);
    }

    private void hideVisitorInfo() {
        photoCard.setVisibility(View.GONE);
        unlockButton.setVisibility(View.GONE);
        photoImageView.setImageDrawable(null);
        currentVisit = null;
    }

    private void setLoadingState(boolean loading) {
        loadingProgress.setVisibility(loading ? View.VISIBLE : View.GONE);
        ringButton.setEnabled(!loading);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (apiService != null) {
            apiService.shutdown();
        }
    }
}
