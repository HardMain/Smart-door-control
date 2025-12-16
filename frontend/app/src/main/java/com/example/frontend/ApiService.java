package com.example.frontend;

import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.io.IOException;
import java.lang.reflect.Type;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class ApiService {
    private static final String TAG = "ApiService";
    private static final String BASE_URL = "http://192.168.0.110:8000";
    private static final String API_KEY = "my-super-secret-key-12345";

    private final OkHttpClient client;
    private final Gson gson;
    private final ExecutorService executorService;
    private final Handler mainHandler;

    public ApiService() {
        this.client = new OkHttpClient();
        this.gson = new Gson();
        this.executorService = Executors.newSingleThreadExecutor();
        this.mainHandler = new Handler(Looper.getMainLooper());
    }

    public interface ApiCallback<T> {
        void onSuccess(T result);
        void onError(String error);
    }

    public void ringDoorbell(ApiCallback<Visit> callback) {
        executorService.execute(() -> {
            try {
                RequestBody body = RequestBody.create("", MediaType.get("application/json; charset=utf-8"));
                Request request = new Request.Builder()
                        .url(BASE_URL + "/doorbell/ring")
                        .post(body)
                        .build();

                try (Response response = client.newCall(request).execute()) {
                    if (response.isSuccessful() && response.body() != null) {
                        String jsonResponse = response.body().string();
                        Log.d(TAG, "Response from backend: " + jsonResponse);
                        Visit visit = gson.fromJson(jsonResponse, Visit.class);
                        Log.d(TAG, "Photo URL: " + visit.getPhotoUrl());
                        mainHandler.post(() -> callback.onSuccess(visit));
                    } else {
                        mainHandler.post(() -> callback.onError("Ошибка сервера: " + response.code()));
                    }
                }
            } catch (IOException e) {
                mainHandler.post(() -> callback.onError("Ошибка сети: " + e.getMessage()));
            }
        });
    }

    public void unlockDoor(ApiCallback<String> callback) {
        executorService.execute(() -> {
            try {
                RequestBody body = RequestBody.create("", MediaType.get("application/json; charset=utf-8"));
                Request request = new Request.Builder()
                        .url(BASE_URL + "/doorbell/unlock")
                        .header("X-Api-Key", API_KEY)
                        .post(body)
                        .build();

                try (Response response = client.newCall(request).execute()) {
                    if (response.isSuccessful()) {
                        mainHandler.post(() -> callback.onSuccess("Дверь открыта!"));
                    } else {
                        mainHandler.post(() -> callback.onError("Ошибка открытия двери: " + response.code()));
                    }
                }
            } catch (IOException e) {
                mainHandler.post(() -> callback.onError("Ошибка сети: " + e.getMessage()));
            }
        });
    }

    public void getVisitHistory(int limit, int offset, ApiCallback<List<Visit>> callback) {
        executorService.execute(() -> {
            try {
                String url = BASE_URL + "/doorbell/history?limit=" + limit + "&offset=" + offset;
                Request request = new Request.Builder()
                        .url(url)
                        .get()
                        .build();

                try (Response response = client.newCall(request).execute()) {
                    if (response.isSuccessful() && response.body() != null) {
                        String jsonResponse = response.body().string();
                        Log.d(TAG, "History response: " + jsonResponse);
                        Type listType = new TypeToken<List<Visit>>(){}.getType();
                        List<Visit> visits = gson.fromJson(jsonResponse, listType);
                        mainHandler.post(() -> callback.onSuccess(visits));
                    } else {
                        mainHandler.post(() -> callback.onError("Ошибка сервера: " + response.code()));
                    }
                }
            } catch (IOException e) {
                mainHandler.post(() -> callback.onError("Ошибка сети: " + e.getMessage()));
            }
        });
    }

    public void shutdown() {
        executorService.shutdown();
    }
}